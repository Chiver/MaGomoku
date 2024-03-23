

let winner = ""; 
let isBlackTurn = true; // Black starts
let boardData = []; 
let round = 0; 
let gameState = "idle"; 
const BOARD_SIZE = 9; 

function refreshBoard(){
    isBlackTurn = true; 
    boardData = []; 
    round = 0; 
    winner = ""; 
    gameState = "idle"; 
}

function placePiece(cell, i) {
    if (!isPlacementValid(i, isBlackTurn)){
        console.log("Placement is not valid"); 
        return; 
    }
    const piece = document.createElement("div");
    let currColor = isBlackTurn ? "black" : "white"
    piece.className = `piece ${currColor}`;
    cell.appendChild(piece);
    boardData.push({
        index: i, 
        color: currColor
    }); 
    isBlackTurn = !isBlackTurn; // Switch turns
    
    if(gameState != "playing"){
        gameState = "playing"; 
    }
    // Check for winning 
    let r = Math.trunc(i / BOARD_SIZE); 
    let c = i % BOARD_SIZE; 
    let msg = document.getElementById("game-message"); 
    if (checkWinningState(r, c, currColor)){
        gameState = "win";
        winner = currColor; 
        msg.innerHTML = `Player ${currColor} wins!`; 
    } else {
        msg.innerText = `Player ${isBlackTurn ? "white" : "black"} is playing`; 
    }
}


function isValidNextLayer(r, c, color, matrix){
    if(r >= 0 && c >= 0 && r < BOARD_SIZE && c < BOARD_SIZE){
        let targetInstance = matrix[r][c]; 
        if(targetInstance[3] === false && targetInstance[2] === color){
            console.log("true");
            return true; 
        }
    }
    return false; 
}

function bfs(r, c, currColor, matrix, dir){
    // matrix[r][c] = [row, col, color, visited]
    // Mark curent node as visited. 
    console.log(matrix)
    matrix[r][c] = [r, c, currColor, true]; 
    
    // Next two nodes to visit. 
    nextLayer = []; 

    // Assemble the next layer given direction
    if(dir === 0){ // dir = 0 => left right 
        if(isValidNextLayer(r, c-1, currColor, matrix)){
            nextLayer.push([r, c-1]); 
        }
        if(isValidNextLayer(r, c+1, currColor, matrix)){
            nextLayer.push([r, c+1]); 
        }
    } else if (dir === 1){ // dir = 1 => up down 
        if(isValidNextLayer(r-1, c, currColor, matrix)){
            nextLayer.push([r-1, c]); 
        }
        if(isValidNextLayer(r+1, c, currColor, matrix)){
            nextLayer.push([r+1, c]); 
        }
    } else if (dir === 2){ // dir = 2 => t_left b_right 
        if(isValidNextLayer(r-1, c-1, currColor, matrix)){
            nextLayer.push([r-1, c-1]); 
        }
        if(isValidNextLayer(r+1, c+1, currColor, matrix)){
            nextLayer.push([r+1, c+1]); 
        }
    } else { // dir = 3 => t_right b_left 
        if(isValidNextLayer(r-1, c+1, currColor, matrix)){
            nextLayer.push([r-1, c+1]); 
        }
        if(isValidNextLayer(r+1, c-1, currColor, matrix)){
            nextLayer.push([r+1, c-1]); 
        }
    }
    console.log(`Current node: (${r}, ${c}), layers: ${nextLayer}`);
    count = 1; 
    nextLayer.forEach(x => {
        count += bfs(x[0], x[1], currColor, matrix, dir); 
    })
    console.log(`Current node: (${r}, ${c}) done with flag ${dir} cnt: ${count}`);
    return count; 
}

function makeBoardMatrix(){
    let matrix = []; 
    // Make appended matrix 
    for (let r=0; r < BOARD_SIZE; r++){
        matrix.push([]); 
        for (let c=0; c<BOARD_SIZE; c++){
            // Row, Col, Visited 
            matrix[r].push([r, c, "", false]); 
        }
    }

    boardData.forEach(x => {
        let row = Math.trunc(x.index / BOARD_SIZE); 
        let col = x.index % BOARD_SIZE; 
        matrix[row][col] = [row, col, x.color, false]; 
    })
    // console.log(matrix);
    return matrix; 
}

function checkWinningState(row, col, currColor){
    console.log(boardData);
    if(bfs(row, col, currColor, makeBoardMatrix(), 0) >= 5 ||
       bfs(row, col, currColor, makeBoardMatrix(), 1) >= 5 || 
       bfs(row, col, currColor, makeBoardMatrix(), 2) >= 5 ||
       bfs(row, col, currColor, makeBoardMatrix(), 3) >= 5){
        return true; 
    } 
    return false; 
}


function isPlacementValid(i, isBlackTurn){
    
    if(gameState === "win"){
        alert("Start a new game!");
        return false; 
    }

    let isValid = true; 
    boardData.forEach(elem => {
        if (elem.index === i){
            isValid = false; 
        }
    }); 
    return isValid; 
}

document.addEventListener("DOMContentLoaded", () => {
    const board = document.getElementById("gomokuBoard");

    // Generate the 9x9 grid
    for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        // cell.addEventListener("click", () => placePiece(cell, i), { once: true });
        cell.addEventListener("click", () => placePiece(cell, i));
        board.appendChild(cell);
    }
});