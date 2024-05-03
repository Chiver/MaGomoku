

let winner = ""; 
let isBlackTurn = true; // Black starts
let boardData = []; 
let round = 0; 
let gameState = "idle"; 
let isComputerBlack = true; 
const BOARD_SIZE = 9; 

function refreshBoard(){
    isBlackTurn = true; 
    boardData = []; 
    round = 0; 
    winner = ""; 
    gameState = "idle"; 
}


function movePiece(row, col){
    console.log("Calling MovePiece");
    $.ajax({
        url: `/move_piece_action?x=${row}&y=${col}`,
        type: 'GET',
        contentType: "application/json",
        dataType: "json",
        success: function(data) {
            console.log(data);         
            // Update the page based on the response if needed
        },
        error: function(xhr, status, error) {
            console.error(error);
            // Handle error
        }
    });
}



function placePiece(i, remote=false) {
    if ((remote && isBlackTurn && isComputerBlack) || 
        (!remote && !isBlackTurn && isComputerBlack)) {
        return; 
    }
    if (!isPlacementValid(i, isBlackTurn)){
        console.log("Placement is not valid"); 
        return; 
    }
    const piece = document.getElementById(`piece_${i}`);
    let currColor = isBlackTurn ? "black" : "white"
    piece.className = `piece ${currColor}`;
    
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
    // Call remove to move gantry
    movePiece(r, c); 
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

/**
 * @deprecated This function is previously used to periodically check if the board has an update. 
 */
function checkUpdateFromBoard(){
    $.ajax({
        url: 'http://localhost:5000/check_update_piece',
        type: 'GET',
        dataType: 'json', // Expect JSON data in response
        success: function(data) {
            console.log("Data fetched successfully:", data);
            
            // if (data.is_Ready == true) {
            //     console.log("is_ready:", data.is_Ready); // True
            //     console.log("x:", data.x); // 1
            //     console.log("y:", data.y); // 3
            //     if (data.is_Ready){
            //         let i = data.x * BOARD_SIZE + data.y; 
            //         placePiece(i);  
            //     } else {
            //         console.log("Endpoint not ready, refetch in 1 sec");
            //     }
            // } else {
            //     console.log("Data not ready yet. Wait for callback"); 
            // } 
        }, 
        error: function(xhr, status, error) {
            console.log(error);
            // Handle error
        }
    });
}

function isValidPlacement(data){
    if (data.status === "false"){
        return false;
    }
    if (
        (isBlackTurn && data.curr === "WHITE") || 
        (!isBlackTurn && data.curr === "BLACK" || 
        (data.x < 0 || data.x >= 8 || data.y < 0 || data.y >= 8))
    ){
        return false; 
    }
    let i = data.x * BOARD_SIZE + data.y; 
    return isPlacementValid(i, isBlackTurn); 
}

function fetchMoveAndUpdateBoard() {
    $.ajax({
        url: "/fetch_physical_move_action",  // Use the correct path as defined in urls.py
        type: "GET",  // Method type
        dataType: "json",  // Expected data type from the server
        success: function(data) {
            if (data.status === "true") {
                // Here you can call your function to update the game board with the new move
                // For example, updateBoard(data.x, data.y, data.curr);
                if(isValidPlacement(data)){
                    let i = data.x * BOARD_SIZE + data.y; 
                    placePiece(i, remote=true); 
                    console.log("New move:", data);
                    return; 
                } else {
                    console.log("Invalid Move: ", data);
                }
                    
            } else {
                console.log("No new moves.");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error fetching move:", status, error);
        }
    });
}

function buildBoardCallBack() {
    const board = document.getElementById("gomokuBoard");

    // Generate the 9x9 grid
    for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        const piece = document.createElement("div");
        piece.className = `piece`;
        piece.id = `piece_${i}`;
        cell.appendChild(piece);
        // cell.addEventListener("click", () => placePiece(cell, i), { once: true });
        cell.addEventListener("click", () => placePiece(i));
        board.appendChild(cell);
    }
}

document.addEventListener("DOMContentLoaded", buildBoardCallBack);




// const SIZE = 15, // 棋盘15*15=225个点
//   W = 50 , // 棋盘格子大小
//   SL = W * (SIZE + 1), // 边长 = 棋盘宽高
//   TOTAL_STEPS = SIZE * SIZE; // 总步数

// /** @type {HTMLCanvasElement} */
// let canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
// canvas.width = canvas.height = SL; // 棋盘宽高 = 边长
// canvas.style.cssText = 'position: absolute; inset: 0; margin: auto; cursor: pointer;';
// document.body.appendChild(canvas);

// // 记录棋盘的黑白棋，15*15的二维数组，初始值：-1，黑棋：1，白棋：2
// let chess = Array.from({ length: SIZE }, () => Array(SIZE).fill(-1)),
//   isBlack = true, // 黑棋先下
//   moveSteps = 0; // 下棋步数

// // 监听棋盘点击位置
// canvas.onclick = e => {
//   let [x, y] = [e.offsetX, e.offsetY].map(p => Math.round(p / W) - 1);
//   if (chess[x]?.[y] !== -1) return alert('该位置不可落子！');
//   drawPiece(x, y, isBlack);
//   chess[x][y] = isBlack ? 1 : 2;
//   isWin(x, y, chess[x][y], chess) ? alert(`${isBlack ? '黑' : '白'}棋赢了!`) :
//     ++moveSteps === TOTAL_STEPS ? alert('游戏结束，平局！') : isBlack = !isBlack;
// }

// // 绘制棋盘（棋盘背景色 && 网格线）
// const drawBoard = () => {
//   ctx.fillStyle = '#E4A751';
//   ctx.fillRect(0, 0, SL, SL);
//   for (let i = 0; i < SIZE; i++) {
//     drawLine(0, i, SIZE - 1, i);
//     drawLine(i, 0, i, SIZE - 1);
//   }
// }

// // 两点连线：(x1, y1) <-> (x2, y2)，设置线条宽度lineWidth和颜色LINE_COLOR
// const drawLine = (x1, y1, x2, y2, lineWidth = 1, lineColor = '#000000') => {
//   ctx.lineWidth = lineWidth;
//   ctx.strokeStyle = lineColor;
//   ctx.beginPath();
//   ctx.moveTo(x1 * W + W, y1 * W + W);
//   ctx.lineTo(x2 * W + W, y2 * W + W);
//   ctx.stroke();
// }

// // 绘制棋子，x、y为坐标，isBlack判断黑白棋
// const drawPiece = (x, y, isBlack) => {
//   ctx.beginPath();
//   ctx.arc(x * W + W, y * W + W, W * 0.4, 0, 2 * Math.PI);
//   ctx.closePath();
//   ctx.fillStyle = isBlack ? 'black' : 'white';
//   ctx.fill();
// }

// // 判断游戏胜负，(x, y)当前下棋坐标，role：黑1白2，chess：棋盘数据，二维数组，黑1白2空位-1
// // const isWin = (x, y, role, chess) => {
// //   for (let [dx, dy] of [[1, 0], [0, 1], [1, 1], [1, -1]]) {
// //     let count = 1, i = 0, j = 0;
// //     while(count < 5 && chess[x + dx * ++i]?.[y + dy * i] === role) count++
// //     while(count < 5 && chess[x - dx * ++j]?.[y - dy * j] === role) count++
// //     if (count === 5) return true
// //   }
// //   return false
// // }

// // 使用some方法进行简化
// const isWin = (x, y, role, chess) => [[1, 0], [0, 1], [1, 1], [1, -1]].some(([dx, dy]) => {
//   let count = 1, i = 0, j = 0;
//   while(count < 5 && chess[x + dx * ++i]?.[y + dy * i] === role) count++
//   while(count < 5 && chess[x - dx * ++j]?.[y - dy * j] === role) count++
//   return count === 5
// })

// window.onload = drawBoard