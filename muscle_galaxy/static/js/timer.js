let timeLeft = 60; // 60秒
let timerId = null;

const display = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');

startBtn.addEventListener('click', () => {
    if (timerId !== null) return; // 二重起動防止
    timerId = setInterval(() => {
        timeLeft--;
        display.textContent = `00:${timeLeft.toString().padStart(2, '0')}`;
        if (timeLeft <= 0) {
            clearInterval(timerId);
            alert('終了！');
        }
    }, 1000);
});

resetBtn.addEventListener('click', () => {
    clearInterval(timerId);
    timerId = null;
    timeLeft = 60;
    display.textContent = "00:60";
});