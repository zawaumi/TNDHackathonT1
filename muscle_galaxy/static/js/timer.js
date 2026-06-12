const timerDataElement = document.getElementById('timer-items-data');
const timerItems = timerDataElement ? JSON.parse(timerDataElement.textContent) : [];
let currentIndex = 0;
let timeLeft = timerItems[0]?.seconds || 60;
let timerId = null;
let recordCreated = false;

const display = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const nextBtn = document.getElementById('next-btn');
const resetBtn = document.getElementById('reset-btn');
const currentLabel = document.getElementById('timer-current');
const notesLabel = document.getElementById('timer-notes');
const progressLabel = document.getElementById('timer-progress');
const recordStatus = document.getElementById('record-status');
const manualSecondsInput = document.getElementById('manual-seconds');

function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    return '';
}

function renderTime() {
    const minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
    const seconds = (timeLeft % 60).toString().padStart(2, '0');
    display.textContent = `${minutes}:${seconds}`;
}

function renderStep() {
    const item = timerItems[currentIndex];
    document.querySelectorAll('.timer-step').forEach((step) => {
        step.classList.toggle('is-active', Number(step.dataset.stepIndex) === currentIndex);
    });
    if (!item) {
        currentLabel.textContent = '完了';
        notesLabel.textContent = '筋トレ記録を開始しています。';
        progressLabel.textContent = `${timerItems.length} / ${timerItems.length}`;
        return;
    }
    currentLabel.textContent = `${item.name} ${item.set_number}/${item.sets} set`;
    notesLabel.textContent = `${item.reps}、${item.notes || 'フォームを優先します。'}`;
    progressLabel.textContent = `${currentIndex + 1} / ${timerItems.length}`;
    
    // 入力欄の値を取得して反映（なければデフォルト60秒）
    const manualValue = manualSecondsInput ? parseInt(manualSecondsInput.value) : 60;
    timeLeft = item.seconds || manualValue || 60;
    
    renderTime();
}

function stopTimer() {
    clearInterval(timerId);
    timerId = null;
    if (startBtn) startBtn.textContent = '再開';
}

async function createWorkoutRecord() {
    if (recordCreated) return;
    recordCreated = true;
    recordStatus.textContent = '筋トレ記録を開始中';
    try {
        const response = await fetch('/timer/record/start/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || '記録に失敗しました');
        recordStatus.textContent = `記録を開始しました: ${data.title}`;
    } catch (error) {
        recordStatus.textContent = error.message;
        recordCreated = false;
    }
}

function advanceStep() {
    stopTimer();
    currentIndex += 1;
    if (currentIndex >= timerItems.length) {
        renderStep();
        createWorkoutRecord();
        if (startBtn) startBtn.disabled = true;
        if (nextBtn) nextBtn.disabled = true;
        return;
    }
    renderStep();
}

// 秒数入力欄のイベントリスナー
if (manualSecondsInput) {
    manualSecondsInput.addEventListener('input', () => {
        const newSeconds = parseInt(manualSecondsInput.value);
        if (!isNaN(newSeconds) && timerId === null) {
            timeLeft = newSeconds;
            renderTime();
        }
    });
}

if (startBtn && resetBtn && display) {
    renderStep();

    startBtn.addEventListener('click', () => {
        if (timerItems.length === 0) return;
        if (timerId !== null) {
            stopTimer();
            return;
        }
        startBtn.textContent = '一時停止';
        timerId = setInterval(() => {
            timeLeft = Math.max(timeLeft - 1, 0);
            renderTime();
            if (timeLeft <= 0) {
                advanceStep();
            }
        }, 1000);
    });

    nextBtn.addEventListener('click', () => {
        if (timerItems.length === 0) return;
        advanceStep();
    });

    resetBtn.addEventListener('click', () => {
        stopTimer();
        currentIndex = 0;
        recordCreated = false;
        recordStatus.textContent = '';
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.textContent = '開始';
        }
        if (nextBtn) nextBtn.disabled = false;
        renderStep();
    });
}