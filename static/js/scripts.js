var height = 6;
var width = 5;

var row = 0;
var col = 0;

var gameOver = false;
let darkTheme = false;
let highContrast = false;
let keyboardOnly = false;

var correctWord = "";

window.onload = async () => {
    await initializeGame();
};

const initializeGame = async () => {
    try {
        const game = await fetch('/api/most_recent_game').then(res => res.json());
        correctWord = game.correct_word;
        row = game.guesses.length;
        gameOver = game.is_completed;

        updateNewGameButtonState(gameOver);
        resetBarColors();

        const rects = document.querySelectorAll('#guessDistributionChart rect[fill="#787c7e"]');
        if (gameOver && rects[row - 1]) {
            rects[row - 1].setAttribute('fill', '#4caf50');
            rects[row - 1].setAttribute('stroke', '#4caf50');
        }

        makeBoard(game);
        makeKeyboard(game);

        const settings = await fetch('/api/get_settings').then(res => res.json());
        darkTheme = settings.dark_mode;
        highContrast = settings.high_contrast;
        keyboardOnly = settings.keyboard_only;

        document.getElementById("darkThemeToggle").checked = darkTheme;
        document.getElementById("highContrastToggle").checked = highContrast;
        document.getElementById("keyboardInputToggle").checked = keyboardOnly;

        toggleClass("dark", darkThemeElements, darkTheme);
        toggleClass("high", highContrastElements, highContrast);
        toggleClass("keyboard-input-only", [], keyboardOnly);
    } catch (error) {
        console.error("Error initializing game:", error);
    }
};


function resetBarColors() {
    document.querySelectorAll('#guessDistributionChart rect[fill="#4caf50"]').forEach(rect => {
        rect.setAttribute('fill', '#787c7e');
        rect.setAttribute('stroke', '#787c7e');
    });
}




function makeBoard(data) {
    const board = document.getElementById("board");
    board.innerHTML = "";
    const guesses = data.guesses || [];

    for (let r = 0; r < height; r++) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "row";

        for (let c = 0; c < width; c++) {
            const tile = document.createElement("span");
            tile.id = `${r}-${c}`;
            tile.className = "tile";

            if (r < guesses.length) {
                const guess = guesses[r];
                tile.innerText = guess[c].toUpperCase();
                tile.classList.add("filled", "revealed", checkGuess(guess, correctWord)[c]);
            }

            rowDiv.appendChild(tile);
        }
        board.appendChild(rowDiv);
    }
}



const makeKeyboard = async (data) => {
    const keyboard = document.getElementById("keyboard");
    keyboard.innerHTML = "";

    const guesses = data.guesses || [];
    const keyboardState = {};

    for (const guess of guesses) {
        const result = checkGuess(guess, correctWord);
        for (let c = 0; c < guess.length; c++) {
            const letter = guess[c].toUpperCase();
            const state = result[c];
            if (!keyboardState[letter]) {
                keyboardState[letter] = state;
            } else {
                if (state === "correct") {
                    keyboardState[letter] = "correct";
                } else if (state === "present" && keyboardState[letter] !== "correct") {
                    keyboardState[letter] = "present";
                }
            }
        }
    }

    let keyboardArray = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
    ];

    for (let i = 0; i < keyboardArray.length; i++) {
        let currRow = keyboardArray[i];
        let keyboardRow = document.createElement("div");

        keyboardRow.classList.add("keyboardRow");

        for (let j = 0; j < currRow.length; j++) {
            let keyTile = document.createElement("span");

            let key = currRow[j];
            keyTile.innerText = key;

            if (key === "ENTER") {
                keyTile.id = "Enter";
                keyTile.classList.add("enterKey");
            } else if (key === "⌫") {
                keyTile.id = "Backspace";
                keyTile.classList.add("backspaceKey");

                keyTile.innerText = "";

                const svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svgElement.setAttribute("aria-hidden", "true");
                svgElement.setAttribute("xmlns", "http://www.w3.org/2000/svg");
                svgElement.setAttribute("height", "20");
                svgElement.setAttribute("viewBox", "0 0 24 24");
                svgElement.setAttribute("width", "20");
                svgElement.classList.add("game-icon");

                const pathElement = document.createElementNS("http://www.w3.org/2000/svg", "path");
                pathElement.setAttribute("fill", "var(--color-tone-1)");
                pathElement.setAttribute(
                    "d",
                    "M22 3H7c-.69 0-1.23.35-1.59.88L0 12l5.41 8.11c.36.53.9.89 1.59.89h15c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H7.07L2.4 12l4.66-7H22v14zm-11.59-2L14 13.41 17.59 17 19 15.59 15.41 12 19 8.41 17.59 7 14 10.59 10.41 7 9 8.41 12.59 12 9 15.59z"
                );

                svgElement.appendChild(pathElement);
                keyTile.appendChild(svgElement);
            } else if ("A" <= key && key <= "Z") {
                keyTile.id = "Key" + key;

                const letterState = keyboardState[key];
                if (letterState) {
                    keyTile.classList.add(letterState);
                }
            }

            keyTile.addEventListener("click", processKey);
            keyTile.classList.add("keyButton");
            keyboardRow.appendChild(keyTile);
        }

        keyboard.appendChild(keyboardRow);
    }
};



function checkGuess(guess, correctWord) {
    const result = Array(width).fill("absent");
    const counts = [...correctWord].reduce((acc, letter) => (acc[letter] = (acc[letter] || 0) + 1, acc), {});

    [...guess].forEach((letter, i) => {
        if (letter === correctWord[i]) {
            result[i] = "correct";
            counts[letter]--;
        }
    });

    [...guess].forEach((letter, i) => {
        if (result[i] === "absent" && counts[letter] > 0) {
            result[i] = "present";
            counts[letter]--;
        }
    });

    return result;
}


document.addEventListener('keyup', (e) => {
    if (!keyboardOnly) {
        processInput(e);
    }
})

function processKey() {
    let e = { "code": this.id };
    processInput(e);
}

async function processInput(e) {
    if (gameOver) return;

    if ("KeyA" <= e.code && e.code <= "KeyZ") {
        if (col < width) {
            const currTile = document.getElementById(`${row}-${col}`);
            if (currTile.innerText === "") {
                currTile.innerText = e.code[3];
                currTile.classList.add("filled");
                col++;
            }
        }
    }
    else if (e.code === "Backspace") {
        if (col > 0) {
            col--;
        }
        const currTile = document.getElementById(`${row}-${col}`);
        currTile.innerText = "";
        currTile.classList.remove("filled");
    }
    else if (e.code === "Enter") {
        if (col < width) {
            showAlert("Not enough letters");
            shakeRow(row);
            return;
        }

        const guess = Array.from({ length: width }, (_, c) =>
            document.getElementById(`${row}-${c}`).innerText.toLowerCase()
        ).join("");

        const isValid = await validateWord(guess);
        if (!isValid) {
            showAlert("Not in word list");
            shakeRow(row);
            return;
        }

        const saved = await saveGuess(guess);
        if (saved.success) {
            const result = checkGuess(guess, correctWord);

            for (let c = 0; c < width; c++) {
                const tile = document.getElementById(`${row}-${c}`);
                tile.classList.add("filled", result[c]);
                tile.classList.add("revealed");
            }

            updateKeyboard(guess, result);

            row++;
            col = 0;

            if (saved.game_over) {
                gameOver = true;
                const messages = ["Genius", "Magnificent", "Impressive", "Splendid", "Great", "Phew"];
                if (saved.guessCount >= 1 && saved.guessCount <= 6) {
                    showAlert(messages[saved.guessCount - 1]);
                }
                updateNewGameButtonState(gameOver);
                setTimeout(() => {
                    openModal(modals.statsModal);
                }, 1000);

                const rects = document.querySelectorAll('#guessDistributionChart rect[fill="#787c7e"]');
                if (rects[row - 1]) {
                    rects[row - 1].setAttribute('fill', '#4caf50');
                    rects[row - 1].setAttribute('stroke', '#4caf50');
                }
            }
        } else {
            alert(saved.error || "Error saving the guess. Please try again.");
        }
    }
}




const updateKeyboard = (guess, result) => {
    for (let i = 0; i < guess.length; i++) {
        const letter = guess[i].toUpperCase();
        const state = result[i];

        const keyTile = document.getElementById(`Key${letter}`);
        if (!keyTile) continue;

        if (state === "correct") {
            keyTile.classList.remove("present", "absent");
            keyTile.classList.add("correct");
        } else if (state === "present" && !keyTile.classList.contains("correct")) {
            keyTile.classList.remove("absent");
            keyTile.classList.add("present");
        } else if (state === "absent" && !keyTile.classList.contains("correct") && !keyTile.classList.contains("present")) {
            keyTile.classList.add("absent");
        }
    }
};



async function validateWord(word) {
    try {
        const response = await fetch('/api/validate_word', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ word }),
        });

        const data = await response.json();
        return data.is_valid || false;
    } catch (error) {
        console.error("Error validating word:", error);
        return false;
    }
}


const saveGuess = async (guess) => {
    try {
        const response = await fetch('/api/save_guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guess }),
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error saving guess:", error);
        return { success: false, error: "Network error." };
    }
};





const updateNewGameButtonState = (isCompleted) => {
    isCompleted ? newGameButton.classList.remove("disabled") : newGameButton.classList.add("disabled")
};

const startNewGame = async () => {
    if (!gameOver) {
        showAlert("Game in progress");
        return;
    }

    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (data.success) {
            clearGrid();
            clearKeyboard();
            await initializeGame();
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('Error starting a new game:', error);
        alert('An error occurred. Please try again.');
    }
};


const newGameButton = document.getElementById("newGameButton");
newGameButton.addEventListener("click", startNewGame);



const clearGrid = () => {
    for (let r = 0; r < height; r++) {
        for (let c = 0; c < width; c++) {
            const tile = document.getElementById(`${r}-${c}`);
            tile.innerText = "";
            tile.className = "tile";
        }
    }
};

const clearKeyboard = () => {
    const keys = document.querySelectorAll(".key-button");
    keys.forEach((key) => {
        key.className = "key-button";
    });
};





let alertStack = [];
let fadeInterval = null;

const showAlert = (message) => {
    if (alertStack.length == 10) {
        return;
    }

    const alertContainer = document.getElementById('alertContainer');

    const alertBox = document.createElement('div');
    alertBox.classList.add('customAlert');
    if (darkTheme) (
        alertBox.classList.add('dark')
    )
    alertBox.innerText = message;

    alertContainer.appendChild(alertBox);
    alertStack.push(alertBox);

    alertBox.classList.add('show');

    resetFadeOut();
};

const resetFadeOut = () => {
    if (fadeInterval) {
        clearInterval(fadeInterval);
        fadeInterval = null;
    }

    if (alertStack.length == 1) {
        fadetime = 1000;
    } else {
        fadetime = 300;
    }

    setTimeout(() => {
        startFadeOut();
    }, fadetime);

};

const startFadeOut = () => {
    if (fadeInterval) return;

    fadeInterval = setInterval(() => {
        if (alertStack.length === 0) {
            clearInterval(fadeInterval);
            fadeInterval = null;
            return;
        }

        const alertBox = alertStack.pop();
        alertBox.classList.remove('show');
        setTimeout(() => {
            alertBox.remove();
        }, 200);
    }, 150);
};



const shakeRow = (rowNum) => {
    const rowElement = document.getElementsByClassName('row')[rowNum];
    rowElement.classList.add('shake');
    setTimeout(() => {
        rowElement.classList.remove('shake');
    }, 500);
};




const modals = {
    infoModal: document.getElementById("infoModal"),
    statsModal: document.getElementById("statsModal"),
    settingsModal: document.getElementById("settingsModal"),
};

const modalButtons = {
    infoButton: document.getElementById("infoButton"),
    statsButton: document.getElementById("statsButton"),
    settingsButton: document.getElementById("settingsButton"),
};

const getStats = async () => {
    try {
        const response = await fetch('/api/get_stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.data;
            document.getElementById("gamesPlayed").innerText = stats.games_played;
            document.getElementById("winRate").innerText = `${Math.round(stats.win_rate * 100)}`;
            document.getElementById("currentStreak").innerText = stats.current_streak;
            document.getElementById("longestStreak").innerText = stats.longest_streak;
        } else {
            console.error("Failed to fetch stats:", data.error);
        }
    } catch (error) {
        console.error("Error fetching stats:", error);
    }
};


function openModal(modal) {
    if (modal === modals.statsModal) {
        getStats();
    }

    modal.style.display = "flex";
    modal.querySelector(".modalContainer")?.classList.remove("slideOut");
}


function closeModalWithAnimation(modal) {
    const modalContainer = modal.querySelector(".modalContainer");
    if (!modalContainer) return;

    modalContainer.classList.add("slideOut");
    modalContainer.addEventListener(
        "animationend",
        () => {
            modal.style.display = "none";
            modalContainer.classList.remove("slideOut");
        },
        { once: true }
    );
}

Object.keys(modalButtons).forEach((buttonKey) => {
    const button = modalButtons[buttonKey];
    const modalKey = buttonKey.replace("Button", "Modal");

    if (button && modals[modalKey]) {
        button.addEventListener("click", (e) => {
            e.preventDefault();
            openModal(modals[modalKey]);
        });
    }
});

document.querySelectorAll(".closeModal").forEach((closeButton) => {
    closeButton.addEventListener("click", () => {
        const modal = closeButton.closest(".modal");
        if (modal) closeModalWithAnimation(modal);
    });
});

window.addEventListener("click", (e) => {
    Object.values(modals).forEach((modal) => {
        if (e.target === modal) {
            closeModalWithAnimation(modal);
        }
    });
});


google.charts.load(43, { packages: ['corechart'] });
google.charts.setOnLoadCallback(() => {
    fetchGuessDistribution();
});

async function fetchGuessDistribution() {
    try {
        const response = await fetch('/api/get_distribution');
        const guessData = await response.json();

        drawChart(guessData);
    } catch (error) {
        console.error('Error fetching guess distribution:', error);
    }
}

function drawChart(guessData) {
    const data = google.visualization.arrayToDataTable([
        ['Guess', 'Distribution', { role: "style" }, { role: 'annotation' }],
        ["1", guessData.one, '#787c7e', guessData.one],
        ["2", guessData.two, '#787c7e', guessData.two],
        ["3", guessData.three, '#787c7e', guessData.three],
        ["4", guessData.four, '#787c7e', guessData.four],
        ["5", guessData.five, '#787c7e', guessData.five],
        ["6", guessData.six, '#787c7e', guessData.six]
    ]);

    const options = {
        allowHtml: true,
        bar: { groupWidth: "75%" },
        legend: { position: "none" },
        height: 140,
        timeline: { showBarLabels: false, showRowLabels: false },
        hAxis: {
            gridlines: { count: 0, color: 'transparent' },
            baseline: 'none',
            textPosition: 'none',
        },
        vAxis: {
            gridlines: { count: 0, color: 'transparent' },
            textStyle: {
                fontSize: 18,
                color: '#000',
                bold: true,
            },
            baseline: 'none',
        },
        annotations: {
            alwaysOutside: false,
            textStyle: {
                fontSize: 14,
                bold: true,
                color: '#ffffff',
            },
            boxStyle: {
                stroke: 'transparent',
                fill: 'transparent',
            },
        },
        enableInteractivity: false,
        chartArea: {
            width: '95%',
            height: '100%',
            left: '5%',
        },
        backgroundColor: "transparent",
    };

    const chart = new google.visualization.BarChart(document.getElementById('guessDistributionChart'));
    chart.draw(data, options);
}






function toggleClass(className, elements, add = true) {
    elements.forEach((selector) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach((element) => {
            if (element) {
                add ? element.classList.add(className) : element.classList.remove(className);
            }
        });

    });

    const rowLabels = document.querySelectorAll('#guessDistributionChart text[x="10"]');
    rowLabels.forEach((label) => {
        label.setAttribute('fill', darkTheme ? '#fff' : '#000');
    });

    const settings = {
        dark_mode: darkTheme,
        high_contrast: highContrast,
        keyboard_only: keyboardOnly
    };

    fetch("/api/set_settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(settings),
    })

}

const darkThemeElements = [
    "body",
    ".appHeader",
    ".appControlsButton",
    ".fill",
    ".keyButton",
    ".modal",
    ".settingsModal",
    ".modalContainer",
    ".settingsModalHeader",
    ".settingsCloseModal",
    ".infoCloseModal",
    ".settingOption",
    ".settingLabel",
    ".settingSubtext",
    ".slider",
    ".settingsModalFooter",
    ".infoModalHeader",
    ".infoModalInstructions",
    ".infoModalSubHeader",
    ".infoModalExample",
    ".infoModalFooter",
    ".backspaceKey",
    ".statsModalHeader",
    ".statsCloseModal",
    ".statsLabel",

];

const highContrastElements = [
    ".tile",
    ".keyButton",
    ".input",
    ".slider"
];

document.getElementById("darkThemeToggle").addEventListener("change", (e) => {
    darkTheme = e.target.checked;
    toggleClass("dark", darkThemeElements, e.target.checked);
});

document.getElementById("highContrastToggle").addEventListener("change", (e) => {
    highContrast = e.target.checked;
    toggleClass("high", highContrastElements, e.target.checked);
});

document.getElementById("keyboardInputToggle").addEventListener("change", (e) => {
    keyboardOnly = e.target.checked;
    toggleClass("keyboardOnly", [], e.target.checked);
});


