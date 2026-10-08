// ==========================================
// SMARTSPEND AI
// BUDGET MODULE
// ==========================================

document.addEventListener("DOMContentLoaded",()=>{

console.log("Budget Module Loaded");

initializeBudget();

});

function initializeBudget(){

const createBtn=document.getElementById("createBudgetBtn");

if(createBtn){

createBtn.addEventListener("click",()=>{

alert("Budget creation form will be connected to Flask backend.");

});

}

animateProgress();

}

function animateProgress(){

const bars=document.querySelectorAll(".progress-fill");

bars.forEach((bar,index)=>{

setTimeout(()=>{

bar.style.width="0%";

},index*200);

});

}