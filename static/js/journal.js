const journalBody = document.getElementById('journal-body');
const journalSubmit = document.getElementById('journal-submit');

journalSubmit.addEventListener('click', async () => {
    if (journalBody.value.trim().length === 0) return;

    const res = await fetch('/api/diaries', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            body: journalBody.value.trim(),
        })
    });
    const data = await res.json();
    console.log(data);
});
