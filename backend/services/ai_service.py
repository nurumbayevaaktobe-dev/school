import google.generativeai as genai
import json
import time
from datetime import datetime, timedelta
from collections import deque
from config import Config
from extensions import cache
import base64
import io
from PIL import Image

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

# Initialize model
model = genai.GenerativeModel('gemini-1.5-flash')

class GeminiAIService:
    """Enhanced AI service with Gemini API"""

    def __init__(self):
        self.rate_limit_window = 60  # seconds
        self.max_requests = 15  # free tier: 15 RPM
        self.request_times = deque()

    def _check_rate_limit(self):
        """Check if we can make a request"""
        now = time.time()
        cutoff = now - self.rate_limit_window

        # Remove old requests
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        if len(self.request_times) >= self.max_requests:
            return False

        self.request_times.append(now)
        return True

    def _make_request(self, prompt, image_data=None, use_cache=True):
        """Make API request with caching and error handling"""

        # Check cache first
        if use_cache:
            cache_key = f"ai_{hash(prompt)}"
            cached = cache.get(cache_key)
            if cached:
                return cached

        # Rate limit check
        if not self._check_rate_limit():
            print("⚠️ Rate limit reached, using fallback")
            return None

        try:
            if image_data:
                # Vision request
                # Decode base64 to PIL Image
                img_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(img_bytes))

                response = model.generate_content([prompt, img])
            else:
                # Text-only request
                response = model.generate_content(prompt)

            result = response.text

            # Cache result
            if use_cache:
                cache.set(cache_key, result, timeout=300)  # 5 min cache

            return result

        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return None

    def analyze_classroom(self, students_data):
        """
        Analyze entire classroom and provide insights

        Args:
            students_data: dict with student metrics

        Returns:
            dict with analysis results
        """

        # Prepare metrics summary
        metrics = {
            'total_students': len(students_data),
            'timestamp': datetime.now().isoformat(),
            'students': []
        }

        for student_id, data in students_data.items():
            metrics['students'].append({
                'name': data.get('name', 'Unknown'),
                'active_time_min': data.get('active_time', 0),
                'idle_time_min': data.get('idle_time', 0),
                'app_switches': data.get('switches', 0),
                'current_app': data.get('current_app', 'Unknown'),
                'violations': data.get('violations', 0),
                'progress': data.get('progress', 0)
            })

        prompt = f"""You are an AI teaching assistant analyzing a classroom in real-time.

CLASSROOM DATA:
{json.dumps(metrics, indent=2)}

Provide a concise analysis in JSON format:
{{
  "engagement_percentage": <number 0-100>,
  "status": "<good|warning|critical>",
  "attention_needed": [
    {{
      "name": "<student name>",
      "reason": "<specific issue>",
      "urgency": "<low|medium|high>",
      "action": "<what teacher should do>"
    }}
  ],
  "positive_moments": [
    "<brief positive observation about specific students>"
  ],
  "class_mood": "<focused|distracted|mixed|struggling>",
  "recommendation": "<one specific action teacher should take RIGHT NOW>",
  "predicted_issues": [
    "<potential problems in next 5-10 minutes>"
  ]
}}

Be specific, actionable, and brief. Focus on students who need help NOW."""

        response = self._make_request(prompt, use_cache=False)

        if response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            except:
                pass

        # Fallback: rule-based analysis
        return self._fallback_classroom_analysis(students_data)

    def check_code_on_screen(self, screenshot_base64, student_name, language='python'):
        """
        Analyze code on student's screen using Vision API

        Args:
            screenshot_base64: base64 encoded screenshot
            student_name: student's name
            language: programming language (python, javascript, etc.)

        Returns:
            dict with code analysis
        """

        prompt = f"""Analyze the code visible on this student's screen.

Student: {student_name}
Expected language: {language}

Respond in JSON format:
{{
  "has_code": <true/false>,
  "language_detected": "<language or 'none'>",
  "status": "<correct|has_issues|error|no_code|off_task>",
  "issues": [
    {{
      "type": "<syntax|logic|style|performance>",
      "description": "<brief issue>",
      "line": <line number or null>,
      "severity": "<low|medium|high>"
    }}
  ],
  "positive_aspects": ["<what student did well>"],
  "suggestions": ["<brief improvement suggestion>"],
  "confidence": <0-100>
}}

Be concise and helpful. If no code is visible, indicate what the student is doing instead."""

        response = self._make_request(prompt, image_data=screenshot_base64, use_cache=False)

        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            except:
                pass

        # Fallback: basic analysis
        return {
            "has_code": False,
            "status": "no_analysis",
            "issues": [],
            "confidence": 0
        }

    def batch_check_code(self, students):
        """
        Check code on multiple student screens in parallel

        Args:
            students: list of dicts with {id, name, screenshot_base64}

        Returns:
            dict categorizing students by code status
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {
            'correct': [],
            'has_issues': [],
            'errors': [],
            'no_code': [],
            'off_task': []
        }

        def check_student(student):
            analysis = self.check_code_on_screen(
                student['screenshot'],
                student['name']
            )
            return {
                'student_id': student['id'],
                'student_name': student['name'],
                'analysis': analysis
            }

        # Limit concurrent requests to avoid rate limits
        max_workers = min(5, len(students))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(check_student, s) for s in students]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    status = result['analysis']['status']

                    if status == 'correct':
                        results['correct'].append(result['student_name'])
                    elif status == 'has_issues':
                        results['has_issues'].append({
                            'name': result['student_name'],
                            'issues': result['analysis']['issues']
                        })
                    elif status == 'error':
                        results['errors'].append({
                            'name': result['student_name'],
                            'issues': result['analysis']['issues']
                        })
                    elif status == 'off_task':
                        results['off_task'].append(result['student_name'])
                    else:
                        results['no_code'].append(result['student_name'])

                except Exception as e:
                    print(f"Error checking student: {e}")

        return results

    def generate_smart_message(self, student_context):
        """
        Generate personalized message suggestions

        Args:
            student_context: dict with student info

        Returns:
            dict with message variants
        """

        prompt = f"""Generate 3 message variants for this student situation:

CONTEXT:
- Name: {student_context.get('name')}
- Current activity: {student_context.get('current_activity', 'Unknown')}
- Distracted for: {student_context.get('distraction_time', 0)} minutes
- Task progress: {student_context.get('progress', 0)}%
- Recent issues: {student_context.get('issues', [])}
- Time left in lesson: {student_context.get('time_left', 30)} minutes
- Student personality: {student_context.get('personality', 'neutral')}

Generate 3 message variants in JSON:
{{
  "encouraging": "<motivating, supportive tone with emoji>",
  "direct": "<clear, neutral reminder>",
  "helpful": "<offer specific help if they seem stuck>"
}}

Rules:
- 1-2 sentences max
- Use student's name
- Be constructive, never punitive
- Include appropriate emoji
- Tailor to their specific situation"""

        response = self._make_request(prompt, use_cache=False)

        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            except:
                pass

        # Fallback messages
        name = student_context.get('name', 'Student')
        return {
            "encouraging": f"💪 {name}, you're doing great! Stay focused!",
            "direct": f"{name}, please return to your assignment.",
            "helpful": f"🙋 {name}, need help? Raise your hand!"
        }

    def _fallback_classroom_analysis(self, students_data):
        """Rule-based fallback when AI is unavailable"""

        total = len(students_data)
        if total == 0:
            return {
                "engagement_percentage": 0,
                "status": "critical",
                "attention_needed": [],
                "positive_moments": [],
                "recommendation": "No students connected"
            }

        # Calculate basic metrics
        working = sum(1 for s in students_data.values() if s.get('violations', 0) == 0)
        engagement = int((working / total) * 100)

        # Determine status
        if engagement >= 75:
            status = "good"
        elif engagement >= 50:
            status = "warning"
        else:
            status = "critical"

        # Find students needing attention
        attention_needed = []
        for student_id, data in students_data.items():
            if data.get('violations', 0) > 0:
                attention_needed.append({
                    "name": data.get('name'),
                    "reason": f"{data.get('violations')} violations detected",
                    "urgency": "medium",
                    "action": "Check their screen"
                })

        return {
            "engagement_percentage": engagement,
            "status": status,
            "attention_needed": attention_needed[:3],  # Top 3
            "positive_moments": [f"{working} students are on task"],
            "recommendation": "Continue monitoring" if status == "good" else "Intervene with distracted students"
        }

# Global AI service instance
ai_service = GeminiAIService()
