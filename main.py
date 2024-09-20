from flask import Flask, request, jsonify, render_template
import os
import cohere

app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize Cohere client with the API key from the environment variable
cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    raise ValueError("Cohere API key not found. Please set the COHERE_API_KEY environment variable.")

co = cohere.Client(cohere_api_key)

@app.route('/')
def home():
    return render_template("templates/index.html")

# Route to generate survey questions
@app.route('/generate_survey', methods=['POST'])
def generate_survey():
    data = request.json
    topic = data.get('topic')
    num_questions = data.get('num_questions')
    question_type = data.get('question_type')

    survey = []

    for i in range(int(num_questions)):
        # First API call: generate the question only
        prompt_for_question = f"Create a question about {topic} for a {question_type} survey."
        try:
            # Generate question first
            response_question = co.generate(
                model='command-xlarge-nightly',
                prompt=prompt_for_question,
                max_tokens=100,
                temperature=0.5,  # Lower temperature for more deterministic outputs
                stop_sequences=["\n"]
            )
            question = response_question.generations[0].text.strip()

            # Based on the question type, generate options
            if question_type.lower() == 'multiple choice':
                prompt_for_options = (f"Create four multiple-choice answer options for the following question: '{question}'. "
                                      "Ensure that options are labeled A, B, C, and D, and are clearly distinct from each other.")
            elif question_type.lower() == 'scale rating':
                prompt_for_options = (f"Create a 1 to 5 scale rating answer for the following question: '{question}'. "
                                      "Ensure 1 = Very Unsatisfied and 5 = Very Satisfied.")

            response_options = co.generate(
                model='command-xlarge-nightly',
                prompt=prompt_for_options,
                max_tokens=100,
                temperature=0.5,  # Lower temperature for consistent answers
                stop_sequences=["\n"]
            )
            options = response_options.generations[0].text.strip()

            # Combine the question and options
            full_question_with_options = f"{question}\n{options}"
            survey.append(full_question_with_options)

        except Exception as e:
            print("Error:", e)
            return jsonify({"error": "An error occurred while generating the survey."}), 500

    return jsonify({"questions": survey})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

