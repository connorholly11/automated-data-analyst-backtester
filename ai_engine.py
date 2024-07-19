import anthropic
import os
import re

class AIEngine:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.input_price_per_1m_tokens = 3.00  # $3.00 per 1M input tokens
        self.output_price_per_1m_tokens = 15.00  # $15.00 per 1M output tokens

    def estimate_tokens(self, text):
        # This is a rough estimation. Actual token count may vary.
        words = re.findall(r'\w+', text)
        return len(words) * 1.3  # Assuming average of 1.3 tokens per word

    def calculate_cost(self, input_tokens, output_tokens):
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_1m_tokens
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_1m_tokens
        return input_cost + output_cost

    def analyze_strategy(self, strategy_data):
        prompt = f"Analyze the following trading strategy data and provide insights:\n\n{strategy_data}\n\nPlease provide:\n1. A summary of the strategy's performance\n2. Key strengths and weaknesses\n3. Suggestions for improvement\n4. Any potential risks or concerns"

        input_tokens = self.estimate_tokens(prompt)

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
        )

        output_tokens = self.estimate_tokens(response.content[0].text)
        cost = self.calculate_cost(input_tokens, output_tokens)

        return response.content[0].text, cost