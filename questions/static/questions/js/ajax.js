function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return null;
}


function redirectToLogin() {
    window.location.href = `/login/?next=${window.location.pathname}`;
}


function sendAjaxPost(url, data) {
    return fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data),
    }).then((response) => {
        if (response.status === 401) {
            redirectToLogin();
            return null;
        }

        return response.json().then((json) => {
            if (!response.ok) {
                throw json;
            }

            return json;
        });
    });
}


function updateVoteButtons(buttonsContainer, activeValue) {
    const activeName = activeValue === 1 ? 'like' : 'dislike';

    buttonsContainer.querySelectorAll('button').forEach((button) => {
        button.classList.toggle(
            'vote_active',
            button.dataset.value === activeName
        );
    });
}


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.js-question-vote').forEach((button) => {
        button.addEventListener('click', () => {
            const questionId = button.dataset.questionId;
            const value = button.dataset.value;
            const url = button.dataset.url;

            sendAjaxPost(url, {
                question_id: questionId,
                value: value,
            })
                .then((data) => {
                    if (!data) {
                        return;
                    }

                    const likesBlock = button.closest('.likes');
                    const rating = likesBlock.querySelector('.likes_count');
                    const buttonsContainer = likesBlock.querySelector('.likes_buttons');

                    rating.textContent = data.rating;
                    updateVoteButtons(buttonsContainer, data.value);
                })
                .catch((error) => {
                    alert(error.message || 'Не удалось оценить вопрос.');
                });
        });
    });

    document.querySelectorAll('.js-answer-vote').forEach((button) => {
        button.addEventListener('click', () => {
            const answerId = button.dataset.answerId;
            const value = button.dataset.value;
            const url = button.dataset.url;

            sendAjaxPost(url, {
                answer_id: answerId,
                value: value,
            })
                .then((data) => {
                    if (!data) {
                        return;
                    }

                    const likesBlock = button.closest('.likes');
                    const rating = likesBlock.querySelector('.likes_count');
                    const buttonsContainer = likesBlock.querySelector('.likes_buttons');

                    rating.textContent = data.rating;
                    updateVoteButtons(buttonsContainer, data.value);
                })
                .catch((error) => {
                    alert(error.message || 'Не удалось оценить ответ.');
                });
        });
    });

    document.querySelectorAll('.js-correct-answer').forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            const questionId = checkbox.dataset.questionId;
            const answerId = checkbox.dataset.answerId;
            const url = checkbox.dataset.url;

            sendAjaxPost(url, {
                question_id: questionId,
                answer_id: answerId,
            })
                .then((data) => {
                    if (!data) {
                        return;
                    }

                    document.querySelectorAll('.js-correct-answer').forEach((item) => {
                        item.checked = false;
                    });

                    const selected = document.querySelector(
                        `.js-correct-answer[data-answer-id="${data.correct_answer_id}"]`
                    );

                    if (selected) {
                        selected.checked = true;
                    }
                })
                .catch((error) => {
                    checkbox.checked = !checkbox.checked;
                    alert(error.message || 'Не удалось выбрать правильный ответ.');
                });
        });
    });
});