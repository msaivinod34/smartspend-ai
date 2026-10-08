// ==========================================
// SMARTSPEND AI
// app.js
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // PASSWORD SHOW / HIDE
    // ==========================================

    const togglePassword = document.getElementById("togglePassword");

    if (togglePassword) {

        togglePassword.addEventListener("click", function () {

            const password = document.getElementById("password");
            const icon = togglePassword.querySelector("i");

            if (password.type === "password") {

                password.type = "text";
                icon.classList.replace("fa-eye", "fa-eye-slash");

            } else {

                password.type = "password";
                icon.classList.replace("fa-eye-slash", "fa-eye");

            }

        });

    }

    // ==========================================
    // CONFIRM PASSWORD SHOW / HIDE
    // ==========================================

    const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");

    if (toggleConfirmPassword) {

        toggleConfirmPassword.addEventListener("click", function () {

            const confirmPassword = document.getElementById("confirmPassword");
            const icon = toggleConfirmPassword.querySelector("i");

            if (confirmPassword.type === "password") {

                confirmPassword.type = "text";
                icon.classList.replace("fa-eye", "fa-eye-slash");

            } else {

                confirmPassword.type = "password";
                icon.classList.replace("fa-eye-slash", "fa-eye");

            }

        });

    }

    // ==========================================
    // PASSWORD STRENGTH
    // ==========================================

    const password = document.getElementById("password");
    const fill = document.getElementById("strengthFill");
    const text = document.getElementById("strengthText");

    if (password && fill && text) {

        password.addEventListener("input", function () {

            const value = password.value;

            let strength = 0;

            if (value.length >= 8) strength++;
            if (/[A-Z]/.test(value)) strength++;
            if (/[0-9]/.test(value)) strength++;
            if (/[^A-Za-z0-9]/.test(value)) strength++;

            const widths = ["0%", "25%", "50%", "75%", "100%"];

            const colors = [
                "#E2E8F0",
                "#EF4444",
                "#F59E0B",
                "#3B82F6",
                "#10B981"
            ];

            const labels = [
                "Password Strength",
                "Weak",
                "Fair",
                "Good",
                "Strong"
            ];

            fill.style.width = widths[strength];
            fill.style.background = colors[strength];
            text.innerText = labels[strength];

        });

    }

    // ==========================================
    // REGISTER API
    // ==========================================

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {

        registerForm.addEventListener("submit", async function (e) {

            e.preventDefault();

            const fullname = document.getElementById("fullname").value.trim();
            const email = document.getElementById("email").value.trim();
            const phone = document.getElementById("phone").value.trim();
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirmPassword").value;

            if (password !== confirmPassword) {

                alert("Passwords do not match.");
                return;

            }

            try {

                const response = await fetch("http://127.0.0.1:5000/api/register", {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json"

                    },

                    body: JSON.stringify({

                        name: fullname,
                        email: email,
                        phone: phone,
                        password: password

                    })

                });

                const result = await response.json();

                alert(result.message);

                if (response.ok) {

                    window.location.href = "login.html";

                }

            }

            catch (error) {

                console.error(error);

                alert("Unable to connect to backend server.");

            }

        });

    }
        // ==========================================
    // LOGIN API
    // ==========================================

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {

        loginForm.addEventListener("submit", async function (e) {

            e.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            if (!email || !password) {

                alert("Please enter email and password.");
                return;

            }

            try {

                const response = await fetch("http://127.0.0.1:5000/api/login", {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json"

                    },

                    body: JSON.stringify({

                        email: email,
                        password: password

                    })

                });

                const result = await response.json();

                if (response.ok) {

                    localStorage.setItem("userEmail", email);
                    localStorage.setItem("userName", result.name);

                    alert(result.message);

                    window.location.href = "dashboard.html";

                } else {

                    alert(result.message);

                }

            }

            catch (error) {

                console.error(error);

                alert("Unable to connect to backend server.");

            }

        });

    }

    // ==========================================
    // PROTECT PAGES
    // ==========================================

    const protectedPages = [

        "dashboard.html",
        "expenses.html",
        "analytics.html",
        "budgets.html",
        "reports.html",
        "ai.html",
        "settings.html",
        "profile.html"

    ];

    const currentPage = window.location.pathname.split("/").pop();

    if (protectedPages.includes(currentPage)) {

        const user = localStorage.getItem("userEmail");

        if (!user) {

            window.location.href = "login.html";

        }

    }

    // ==========================================
    // LOAD USER
    // ==========================================

    const userName = localStorage.getItem("userName");
    const userEmail = localStorage.getItem("userEmail");

    // Dashboard Welcome

    const welcomeUser = document.getElementById("welcomeUser");

    if (welcomeUser && userName) {

        welcomeUser.innerHTML = "Welcome Back, " + userName + " 👋";

    }

    // Dashboard Avatar

    const dashboardAvatar = document.getElementById("dashboardAvatar");

    if (dashboardAvatar && userName) {

        dashboardAvatar.src =
            "https://ui-avatars.com/api/?name=" +
            encodeURIComponent(userName) +
            "&background=2563EB&color=ffffff&size=200";

    }

    // Profile Name

    const profileName = document.getElementById("profileName");

    if (profileName && userName) {

        profileName.innerHTML = userName;

    }

    // Profile Email

    const profileEmail = document.getElementById("profileEmail");

    if (profileEmail && userEmail) {

        profileEmail.innerHTML = userEmail;

    }
        // ==========================================
    // PROFILE IMAGE
    // ==========================================

    const profileImage = document.getElementById("profileImage");

    if (profileImage && userName) {

        profileImage.src =
            "https://ui-avatars.com/api/?name=" +
            encodeURIComponent(userName) +
            "&background=2563EB&color=ffffff&size=256";

    }

    // ==========================================
    // SETTINGS PAGE
    // ==========================================

    const settingsUserName = document.getElementById("settingsUserName");
    const settingsUserEmail = document.getElementById("settingsUserEmail");

    if (settingsUserName && userName) {

        settingsUserName.textContent = userName;

    }

    if (settingsUserEmail && userEmail) {

        settingsUserEmail.textContent = userEmail;

    }

    // ==========================================
    // LOGOUT
    // ==========================================

    const logoutButtons = document.querySelectorAll(".logout-btn");

    logoutButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            if (confirm("Are you sure you want to logout?")) {

                localStorage.removeItem("userName");
                localStorage.removeItem("userEmail");

                window.location.href = "login.html";

            }

        });

    });

    // ==========================================
    // HELPER FUNCTION
    // ==========================================

    function isLoggedIn() {

        return localStorage.getItem("userEmail") !== null;

    }

    console.log("SmartSpend AI Loaded Successfully");

});