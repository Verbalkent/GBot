document.getElementById('surveyForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const topic = document.getElementById('topic').value;
    const numQuestions = document.getElementById('numQuestions').value;
    const questionType = document.getElementById('questionType').value;

    const response = await fetch('/generate_survey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, num_questions: numQuestions, question_type: questionType }),
    });

    const data = await response.json();
    document.getElementById('surveyOutput').innerHTML = `<pre>${data.questions}</pre>`;
});
