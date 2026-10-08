// ==========================================
// SMARTSPEND AI ASSISTANT
// REAL ML INTEGRATION
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    initializeAI();

});


// ==========================================
// INITIALIZE AI
// ==========================================

function initializeAI() {

    const input = document.querySelector(".chat-input input");
    const button = document.querySelector(".chat-input button");
    const body = document.querySelector(".chat-body");

    if (!input || !body) {
        console.log("AI chat elements not found.");
        return;
    }


    // ==========================================
    // SEND BUTTON
    // ==========================================

    if (button) {

        button.addEventListener("click", () => {

            sendMessage(
                input,
                body
            );

        });

    }


    // ==========================================
    // ENTER KEY
    // ==========================================

    input.addEventListener("keypress", (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage(
                input,
                body
            );

        }

    });


    // ==========================================
    // QUICK BUTTONS
    // ==========================================

    const quickButtons =
        document.querySelectorAll(".btn-outline");


    quickButtons.forEach(button => {

        button.addEventListener("click", () => {

            input.value =
                button.innerText;

            input.focus();

        });

    });

}


// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage(input, body) {

    const message =
        input.value.trim();


    if (message === "") {

        return;

    }


    // ==========================================
    // SHOW USER MESSAGE
    // ==========================================

    const userMessage =
        document.createElement("div");

    userMessage.className =
        "ai-message user-message";

    userMessage.innerText =
        message;

    body.appendChild(
        userMessage
    );


    input.value = "";


    body.scrollTop =
        body.scrollHeight;


    // ==========================================
    // SHOW THINKING MESSAGE
    // ==========================================

    const thinking =
        document.createElement("div");

    thinking.className =
        "ai-message";

    thinking.innerText =
        "Analyzing your spending data...";

    body.appendChild(
        thinking
    );


    body.scrollTop =
        body.scrollHeight;


    try {

        // ==========================================
        // GET USER EMAIL
        // ==========================================

        const userEmail =
            getUserEmail();


        if (!userEmail) {

            throw new Error(
                "User email not found."
            );

        }


        // ==========================================
        // GET FINANCIAL DATA
        // ==========================================

        const financialData =
            await getFinancialData(
                userEmail
            );


        // ==========================================
        // CHECK DATA
        // ==========================================

        if (!financialData) {

            throw new Error(
                "Unable to load financial data."
            );

        }


        // ==========================================
        // SEND DATA TO REAL ML MODEL
        // ==========================================

        const prediction =
            await getMLPrediction(
                financialData
            );


        // ==========================================
        // REMOVE THINKING MESSAGE
        // ==========================================

        thinking.remove();


        // ==========================================
        // DISPLAY REAL AI RESULT
        // ==========================================

        const aiMessage =
            document.createElement("div");

        aiMessage.className =
            "ai-message";


        aiMessage.innerHTML =

            `
            <strong>SmartSpend AI</strong>
            <br><br>

            Based on your historical spending data,
            the predicted expense for next month is:

            <br><br>

            <strong>
                ₹${prediction.prediction.toLocaleString(
                    "en-IN",
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }
                )}
            </strong>

            <br><br>

            <small>
                Prediction generated using the
                Extra Trees Regressor model.
            </small>
            `;


        body.appendChild(
            aiMessage
        );


        body.scrollTop =
            body.scrollHeight;


    }
    catch (error) {

        console.error(
            "AI ERROR:",
            error
        );


        thinking.remove();


        const errorMessage =
            document.createElement("div");

        errorMessage.className =
            "ai-message";


        errorMessage.innerHTML =

            `
            <strong>SmartSpend AI</strong>
            <br><br>
            I could not generate the prediction.
            <br><br>
            <small>
                ${error.message}
            </small>
            `;


        body.appendChild(
            errorMessage
        );


        body.scrollTop =
            body.scrollHeight;

    }

}


// ==========================================
// GET USER EMAIL
// ==========================================

function getUserEmail() {

    // ------------------------------------------
    // Try localStorage
    // ------------------------------------------

    const possibleKeys = [

        "userEmail",
        "email",
        "loggedInUser",
        "user"

    ];


    for (const key of possibleKeys) {

        const value =
            localStorage.getItem(
                key
            );


        if (!value) {

            continue;

        }


        // ------------------------------------------
        // Normal email
        // ------------------------------------------

        if (
            typeof value === "string"
            &&
            value.includes("@")
        ) {

            return value;

        }


        // ------------------------------------------
        // JSON user object
        // ------------------------------------------

        try {

            const user =
                JSON.parse(value);


            if (
                user
                &&
                user.email
            ) {

                return user.email;

            }

        }
        catch {

            // Ignore invalid JSON

        }

    }


    return null;

}


// ==========================================
// GET FINANCIAL DATA
// ==========================================

async function getFinancialData(
    userEmail
) {

    // ==========================================
    // GET ALL EXPENSES
    // ==========================================

    const response =
        await fetch(

            `http://127.0.0.1:5000/api/expenses?userEmail=${encodeURIComponent(
                userEmail
            )}`

        );


    if (!response.ok) {

        throw new Error(
            "Unable to load expenses."
        );

    }


    const expenses =
        await response.json();


    // ==========================================
    // CHECK EXPENSES
    // ==========================================

    if (
        !Array.isArray(expenses)
        ||
        expenses.length === 0
    ) {

        return {

            totalExpense: 0,

            transactionCount: 0,

            averageExpense: 0,

            food: 0,

            shopping: 0,

            transport: 0,

            fuel: 0,

            travel: 0,

            bills: 0,

            medical: 0,

            education: 0,

            entertainment: 0,

            investment: 0,

            emi: 0,

            others: 0

        };

    }


    // ==========================================
    // INITIALIZE VALUES
    // ==========================================

    let totalExpense = 0;

    let categoryTotals = {

        Food: 0,

        Shopping: 0,

        Transport: 0,

        Fuel: 0,

        Travel: 0,

        Bills: 0,

        Medical: 0,

        Education: 0,

        Entertainment: 0,

        Investment: 0,

        EMI: 0,

        Others: 0

    };


    // ==========================================
    // PROCESS EXPENSES
    // ==========================================

    expenses.forEach(expense => {

        const amount =
            Number(
                expense.amount || 0
            );


        totalExpense +=
            amount;


        const category =
            expense.category || "Others";


        if (
            categoryTotals[
                category
            ] !== undefined
        ) {

            categoryTotals[
                category
            ] += amount;

        }
        else {

            categoryTotals.Others +=
                amount;

        }

    });


    // ==========================================
    // AVERAGE EXPENSE
    // ==========================================

    const averageExpense =
        totalExpense /
        expenses.length;


    // ==========================================
    // RETURN MODEL FEATURES
    // ==========================================

    return {

        totalExpense:
            totalExpense,

        transactionCount:
            expenses.length,

        averageExpense:
            averageExpense,

        food:
            categoryTotals.Food,

        shopping:
            categoryTotals.Shopping,

        transport:
            categoryTotals.Transport,

        fuel:
            categoryTotals.Fuel,

        travel:
            categoryTotals.Travel,

        bills:
            categoryTotals.Bills,

        medical:
            categoryTotals.Medical,

        education:
            categoryTotals.Education,

        entertainment:
            categoryTotals.Entertainment,

        investment:
            categoryTotals.Investment,

        emi:
            categoryTotals.EMI,

        others:
            categoryTotals.Others

    };

}


// ==========================================
// CALL REAL ML MODEL
// ==========================================

async function getMLPrediction(
    financialData
) {

    const response =
        await fetch(

            "http://127.0.0.1:5000/api/ml/predict",

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(
                        financialData
                    )

            }

        );


    if (!response.ok) {

        let errorMessage =
            "ML prediction failed.";


        try {

            const error =
                await response.json();


            if (error.message) {

                errorMessage =
                    error.message;

            }

        }
        catch {

            // Ignore JSON parsing error

        }


        throw new Error(
            errorMessage
        );

    }


    const result =
        await response.json();


    if (
        !result.success
    ) {

        throw new Error(
            result.message ||
            "Prediction failed."
        );

    }


    return result;

}