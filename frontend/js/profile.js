// ==========================================
// PROFILE MODULE
// ==========================================

document.addEventListener("DOMContentLoaded",()=>{

console.log("Profile Loaded");

const save=document.querySelector(".save-profile");

if(save){

save.addEventListener("click",()=>{

alert("Profile will be updated after backend integration.");

});

}

const photo=document.querySelector(".profile-card button");

if(photo){

photo.addEventListener("click",()=>{

alert("Profile photo upload will be available after backend integration.");

});

}

const logout=document.querySelector(".logout-btn");

if(logout){

logout.addEventListener("click",()=>{

if(confirm("Do you want to logout?")){

window.location.href="login.html";

}

});

}

});