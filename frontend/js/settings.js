// =====================================
// SMARTSPEND SETTINGS
// =====================================

document.addEventListener("DOMContentLoaded",()=>{

console.log("Settings Loaded");

const logout=document.querySelector(".logout-btn");

if(logout){

logout.addEventListener("click",()=>{

if(confirm("Are you sure you want to sign out?")){

window.location.href="login.html";

}

});

}

const switches=document.querySelectorAll(".switch input");

switches.forEach(toggle=>{

toggle.addEventListener("change",()=>{

console.log("Setting Updated");

});

});

const currency=document.querySelector("select");

if(currency){

currency.addEventListener("change",()=>{

console.log("Currency:",currency.value);

});

}

const securityItems=document.querySelectorAll(".security-item");

securityItems.forEach(item=>{

item.addEventListener("click",()=>{

alert(item.innerText + " page will be connected after Flask backend.");

});

});

});