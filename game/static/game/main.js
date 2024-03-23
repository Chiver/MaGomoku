



document.addEventListener("DOMContentLoaded", () => {
    const board = document.getElementById("gomokuBoard");
    let isBlackTurn = true; // Black starts

    // Generate the 9x9 grid
    for (let i = 0; i < 81; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.addEventListener("click", () => placePiece(cell), { once: true });
        board.appendChild(cell);
    }

    function placePiece(cell) {
        const piece = document.createElement("div");
        piece.className = `piece ${isBlackTurn ? "black" : "white"}`;
        cell.appendChild(piece);
        isBlackTurn = !isBlackTurn; // Switch turns
    }
});
