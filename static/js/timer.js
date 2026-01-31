// -----------------------------
// DATA & STATE
// -----------------------------
let tasks = TASKS;
let currentTaskIndex = 0;

let timer = null;
let timeLeft = 0;
let isPaused = false;

let state = "idle"; // idle | focus | rest | completed

const REST_MINUTES = 5;

// -----------------------------
// DOM ELEMENTS
// -----------------------------
const taskTitle = document.getElementById("current-task");
const timerDisplay = document.getElementById("timer-display");
const timerState = document.getElementById("timer-state");
const startBtn = document.getElementById("start-btn");
const pauseBtn = document.getElementById("pause-btn");
const skipBtn = document.getElementById("skip-btn");

// -----------------------------
// HELPERS
// -----------------------------
function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// -----------------------------
// TIMER STARTERS
// -----------------------------
function startFocus(task) {
    state = "focus";
    isPaused = false;
    pauseBtn.textContent = "Pause";

    timeLeft = task.focus_minutes * 60;

    taskTitle.textContent = task.title;
    timerState.textContent = "Focus Time";
    timerDisplay.textContent = formatTime(timeLeft);

    startTimer();
}

function startRest() {
    state = "rest";
    isPaused = false;
    pauseBtn.textContent = "Pause";

    timeLeft = REST_MINUTES * 60;

    taskTitle.textContent = "Rest";
    timerState.textContent = "Rest Time";
    timerDisplay.textContent = formatTime(timeLeft);

    startTimer();
}

// -----------------------------
// CORE TIMER LOOP
// -----------------------------
function startTimer() {
    clearInterval(timer); // prevent stacked intervals

    pauseBtn.disabled = false;
    skipBtn.disabled = false;

    timer = setInterval(() => {
        if (!isPaused) {
            timeLeft--;
            timerDisplay.textContent = formatTime(timeLeft);

            if (timeLeft <= 0) {
                clearInterval(timer);
                handleTimerEnd();
            }
        }
    }, 1000);
}

// -----------------------------
// TIMER END HANDLER
// -----------------------------
function handleTimerEnd() {
    if (state === "focus") {
        const finishedTask = tasks[currentTaskIndex];

        // notify backend that task is completed
        fetch("/api/complete-task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task_id: finishedTask.id
            })
        });

        startRest();
    } 
    else if (state === "rest") {
        currentTaskIndex++;

        if (currentTaskIndex < tasks.length) {
            startFocus(tasks[currentTaskIndex]);
        } else {
            finishAll();
        }
    }
}

// -----------------------------
// FINISH ALL TASKS
// -----------------------------
function finishAll() {
    state = "completed";

    taskTitle.textContent = "All tasks completed 🎉";
    timerState.textContent = "Done";
    timerDisplay.textContent = "00:00";

    pauseBtn.disabled = true;
    skipBtn.disabled = true;

    // refresh to show completed tasks
    setTimeout(() => {
        location.reload();
    }, 1500);
}

// -----------------------------
// BUTTON EVENTS
// -----------------------------
startBtn.addEventListener("click", () => {
    if (tasks.length === 0) {
        alert("No tasks to start");
        return;
    }

    startBtn.disabled = true;
    startFocus(tasks[currentTaskIndex]);
});

pauseBtn.addEventListener("click", () => {
    isPaused = !isPaused;
    pauseBtn.textContent = isPaused ? "Resume" : "Pause";
});

skipBtn.addEventListener("click", () => {
    clearInterval(timer);

    if (state === "focus") {
        startRest();
    } else {
        handleTimerEnd();
    }
});
