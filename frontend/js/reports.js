// =========================================================
// SMARTSPEND AI
// NEXT MONTH EXPENSE PREDICTION
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializePrediction();

    }
);


// =========================================================
// INITIALIZE
// =========================================================

function initializePrediction() {

    const button =
        document.getElementById(
            "refreshPredictionBtn"
        );

    if (button) {

        button.addEventListener(
            "click",
            generatePrediction
        );

    }

    generatePrediction();

}


// =========================================================
// GET USER EMAIL
// =========================================================

function getUserEmail() {

    const possibleKeys = [

        "userEmail",
        "email",
        "user_email",
        "loggedInUserEmail"

    ];

    for (const key of possibleKeys) {

        const value =
            localStorage.getItem(key);

        if (value) {

            return value;

        }

    }

    return null;
}


// =========================================================
// GENERATE PREDICTION
// =========================================================

async function generatePrediction() {

    const predictionElement =
        document.getElementById(
            "nextMonthPrediction"
        );

    const statusElement =
        document.getElementById(
            "predictionStatus"
        );

    const modelStatus =
        document.getElementById(
            "predictionModelStatus"
        );

    const button =
        document.getElementById(
            "refreshPredictionBtn"
        );


    if (!predictionElement) {

        return;

    }


    const email =
        getUserEmail();


    // -----------------------------------------------------
    // CHECK EMAIL
    // -----------------------------------------------------

    if (!email) {

        predictionElement.innerText =
            "Unavailable";

        statusElement.innerText =
            "User email was not found. Please login again.";

        modelStatus.innerText =
            "No User";

        return;

    }


    // -----------------------------------------------------
    // LOADING
    // -----------------------------------------------------

    predictionElement.innerText =
        "Calculating...";

    statusElement.innerText =
        "Analyzing your expense history...";

    modelStatus.innerText =
        "Processing";


    if (button) {

        button.disabled = true;

        button.innerHTML =
            `<i class="fa-solid fa-spinner fa-spin"></i>
             Predicting...`;

    }


    try {

        // -------------------------------------------------
        // SEND USER EMAIL ONLY
        // BACKEND FETCHES REAL DATA FROM MONGODB
        // -------------------------------------------------

        const response =
            await fetch(
                "/api/ml/predict",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            userEmail:
                                email

                        })

                }
            );


        const result =
            await response.json();


        console.log(
            "Prediction response:",
            result
        );


        if (!response.ok) {

            throw new Error(
                result.message ||
                result.error ||
                "Prediction failed."
            );

        }


        if (
            !result.success
        ) {

            throw new Error(
                result.message ||
                "Prediction failed."
            );

        }


        // -------------------------------------------------
        // DISPLAY PREDICTION
        // -------------------------------------------------

        const prediction =
            Number(
                result.prediction
            );


        if (
            !Number.isFinite(
                prediction
            )
        ) {

            throw new Error(
                "Invalid prediction returned by server."
            );

        }


        predictionElement.innerText =
            "₹" +
            prediction.toLocaleString(
                "en-IN",
                {

                    minimumFractionDigits:
                        2,

                    maximumFractionDigits:
                        2

                }
            );


        // -------------------------------------------------
        // STATUS
        // -------------------------------------------------

        statusElement.innerText =
            "Prediction generated from your expense history.";


        modelStatus.innerText =
            result.model ||
            "Extra Trees Regressor";


        console.log(
            "Current expenses:",
            result.currentMonthExpenses
        );

        console.log(
            "Previous month:",
            result.previousMonthExpenses
        );

        console.log(
            "Three month average:",
            result.threeMonthAverage
        );

        console.log(
            "Transactions:",
            result.transactionCount
        );


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        predictionElement.innerText =
            "Unavailable";


        statusElement.innerText =
            error.message ||
            "Unable to generate prediction.";


        modelStatus.innerText =
            "Unavailable";

    }


    // -----------------------------------------------------
    // RESET BUTTON
    // -----------------------------------------------------

    if (button) {

        button.disabled = false;

        button.innerHTML =
            `<i class="fa-solid fa-rotate"></i>
             Generate Prediction`;

    }

}
// =========================================================
// SMARTSPEND AI
// NEXT MONTH EXPENSE PREDICTION
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializePrediction();

    }
);


// =========================================================
// INITIALIZE
// =========================================================

function initializePrediction() {

    const button =
        document.getElementById(
            "refreshPredictionBtn"
        );

    if (button) {

        button.addEventListener(
            "click",
            generatePrediction
        );

    }

    generatePrediction();

}


// =========================================================
// GET USER EMAIL
// =========================================================

function getUserEmail() {

    const possibleKeys = [

        "userEmail",
        "email",
        "user_email",
        "loggedInUserEmail",
        "user_email_address"

    ];


    // -----------------------------------------------------
    // LOCAL STORAGE
    // -----------------------------------------------------

    for (const key of possibleKeys) {

        const value =
            localStorage.getItem(key);

        if (
            value &&
            value !== "null" &&
            value !== "undefined"
        ) {

            return value
                .toString()
                .trim()
                .toLowerCase();

        }

    }


    // -----------------------------------------------------
    // SESSION STORAGE
    // -----------------------------------------------------

    for (const key of possibleKeys) {

        const value =
            sessionStorage.getItem(key);

        if (
            value &&
            value !== "null" &&
            value !== "undefined"
        ) {

            return value
                .toString()
                .trim()
                .toLowerCase();

        }

    }


    // -----------------------------------------------------
    // CHECK OBJECT STORAGE
    // -----------------------------------------------------

    const objectKeys = [

        "user",
        "currentUser",
        "loggedInUser"

    ];


    for (const key of objectKeys) {

        try {

            const raw =
                localStorage.getItem(key);

            if (!raw) {
                continue;
            }

            const user =
                JSON.parse(raw);

            if (
                user &&
                user.email
            ) {

                return user.email
                    .toString()
                    .trim()
                    .toLowerCase();

            }

            if (
                user &&
                user.userEmail
            ) {

                return user.userEmail
                    .toString()
                    .trim()
                    .toLowerCase();

            }

        } catch (error) {

            console.log(
                "Unable to parse stored user:",
                key
            );

        }

    }


    return null;

}


// =========================================================
// GENERATE PREDICTION
// =========================================================

async function generatePrediction() {

    const predictionElement =
        document.getElementById(
            "nextMonthPrediction"
        );

    const statusElement =
        document.getElementById(
            "predictionStatus"
        );

    const modelStatus =
        document.getElementById(
            "predictionModelStatus"
        );

    const button =
        document.getElementById(
            "refreshPredictionBtn"
        );


    // -----------------------------------------------------
    // CHECK ELEMENT
    // -----------------------------------------------------

    if (!predictionElement) {

        console.error(
            "nextMonthPrediction element not found."
        );

        return;

    }


    // -----------------------------------------------------
    // GET EMAIL
    // -----------------------------------------------------

    const email =
        getUserEmail();


    console.log(
        "Prediction user email:",
        email
    );


    // -----------------------------------------------------
    // EMAIL NOT FOUND
    // -----------------------------------------------------

    if (!email) {

        predictionElement.innerText =
            "Unavailable";

        if (statusElement) {

            statusElement.innerText =
                "User email was not found. Please login again.";

        }

        if (modelStatus) {

            modelStatus.innerText =
                "No User";

        }

        return;

    }


    // -----------------------------------------------------
    // LOADING
    // -----------------------------------------------------

    predictionElement.innerText =
        "Calculating...";


    if (statusElement) {

        statusElement.innerText =
            "Analyzing your expense history...";

    }


    if (modelStatus) {

        modelStatus.innerText =
            "Processing";

    }


    if (button) {

        button.disabled = true;

        button.innerHTML =
            `<i class="fa-solid fa-spinner fa-spin"></i>
             Predicting...`;

    }


    try {

        // -------------------------------------------------
        // CREATE URL
        //
        // We send the email BOTH:
        // 1. In JSON
        // 2. In query parameter
        //
        // This makes the request robust.
        // -------------------------------------------------

        const url =
            `/api/ml/predict?userEmail=${encodeURIComponent(email)}`;


        console.log(
            "Prediction API URL:",
            url
        );


        // -------------------------------------------------
        // API REQUEST
        // -------------------------------------------------

        const response =
            await fetch(
                url,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    cache:
                        "no-store",

                    body:
                        JSON.stringify({

                            userEmail:
                                email,

                            email:
                                email

                        })

                }
            );


        // -------------------------------------------------
        // READ RESPONSE
        // -------------------------------------------------

        const result =
            await response.json();


        console.log(
            "Prediction HTTP status:",
            response.status
        );


        console.log(
            "Prediction response:",
            result
        );


        // -------------------------------------------------
        // BACKEND ERROR
        // -------------------------------------------------

        if (!response.ok) {

            throw new Error(
                result.message ||
                result.error ||
                `Prediction API failed with status ${response.status}`
            );

        }


        // -------------------------------------------------
        // SUCCESS CHECK
        // -------------------------------------------------

        if (
            result.success !== true
        ) {

            throw new Error(
                result.message ||
                result.error ||
                "Prediction failed."
            );

        }


        // -------------------------------------------------
        // GET PREDICTION
        // -------------------------------------------------

        const prediction =
            Number(
                result.prediction
            );


        if (
            !Number.isFinite(
                prediction
            )
        ) {

            throw new Error(
                "Backend returned an invalid prediction."
            );

        }


        // -------------------------------------------------
        // DISPLAY PREDICTION
        // -------------------------------------------------

        predictionElement.innerText =
            "₹" +
            prediction.toLocaleString(
                "en-IN",
                {

                    minimumFractionDigits:
                        2,

                    maximumFractionDigits:
                        2

                }
            );


        // -------------------------------------------------
        // STATUS
        // -------------------------------------------------

        if (statusElement) {

            statusElement.innerText =
                "Prediction generated from your expense history.";

        }


        // -------------------------------------------------
        // MODEL
        // -------------------------------------------------

        if (modelStatus) {

            modelStatus.innerText =
                result.model ||
                "Extra Trees Regressor";

        }


        // -------------------------------------------------
        // LOG DATA
        // -----------------------------------------------------

        console.log(
            "======================================"
        );

        console.log(
            "SMARTSPEND AI PREDICTION"
        );

        console.log(
            "User:",
            email
        );

        console.log(
            "Prediction:",
            result.prediction
        );

        console.log(
            "Current Month Expenses:",
            result.currentMonthExpenses
        );

        console.log(
            "Expected Change:",
            result.expectedChangePercent
        );

        console.log(
            "Transactions:",
            result.expenseTransactions
        );

        console.log(
            "Model:",
            result.model
        );

        console.log(
            "======================================"
        );


    } catch (error) {

        // -------------------------------------------------
        // ERROR
        // -------------------------------------------------

        console.error(
            "Prediction error:",
            error
        );


        predictionElement.innerText =
            "Unavailable";


        if (statusElement) {

            statusElement.innerText =
                error.message ||
                "Unable to generate prediction.";

        }


        if (modelStatus) {

            modelStatus.innerText =
                "Unavailable";

        }

    }


    // -----------------------------------------------------
    // RESET BUTTON
    // -----------------------------------------------------

    if (button) {

        button.disabled = false;

        button.innerHTML =
            `<i class="fa-solid fa-rotate"></i>
             Generate Prediction`;

    }

}