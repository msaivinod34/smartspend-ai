// =====================================================
// SMARTSPEND AI - INCOME
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("SMARTSPEND AI - Income page loaded");

    const form = document.getElementById("incomeForm");

    if (!form) {
        console.error("incomeForm not found");
        return;
    }

    console.log("incomeForm found");

    form.addEventListener("submit", addIncome);

    loadIncome();

});


// =====================================================
// ADD INCOME
// =====================================================

async function addIncome(event) {

    event.preventDefault();

    console.log("ADD INCOME CLICKED");

    const userEmail =
        localStorage.getItem("userEmail") ||
        localStorage.getItem("email");

    console.log("USER EMAIL:", userEmail);

    if (!userEmail) {

        alert("User email not found. Please login again.");

        return;
    }


    // Get the ACTUAL IDs from income.html

    const amount =
        document.getElementById("amount");

    const incomeType =
        document.getElementById("incomeType");

    const source =
        document.getElementById("source");

    const incomeDate =
        document.getElementById("incomeDate");

    const description =
        document.getElementById("description");

    const recurring =
        document.getElementById("recurring");


    console.log("Amount:", amount);
    console.log("Income Type:", incomeType);
    console.log("Source:", source);
    console.log("Date:", incomeDate);
    console.log("Description:", description);
    console.log("Recurring:", recurring);


    if (
        !amount ||
        !incomeType ||
        !source ||
        !incomeDate ||
        !description
    ) {

        console.error(
            "One or more income form elements were not found."
        );

        alert(
            "Income form is not connected correctly."
        );

        return;
    }


    const amountValue =
        parseFloat(amount.value);

    const typeValue =
        incomeType.value;

    const sourceValue =
        source.value.trim();

    const dateValue =
        incomeDate.value;

    const descriptionValue =
        description.value.trim();

    const recurringValue =
        recurring
            ? recurring.checked
            : false;


    // =================================================
    // VALIDATION
    // =================================================

    if (
        isNaN(amountValue) ||
        amountValue <= 0
    ) {

        alert("Please enter a valid income amount.");

        return;
    }


    if (!typeValue) {

        alert("Please select an income type.");

        return;
    }


    if (!sourceValue) {

        alert("Please enter an income source.");

        return;
    }


    if (!dateValue) {

        alert("Please select an income date.");

        return;
    }


    // =================================================
    // DATA FOR FLASK
    // =================================================

    const incomeData = {

        source: sourceValue,

        category: typeValue,

        amount: amountValue,

        date: dateValue,

        description: descriptionValue,

        userEmail: userEmail,

        recurring: recurringValue

    };


    console.log(
        "SENDING INCOME:",
        incomeData
    );


    // =================================================
    // SEND TO BACKEND
    // =================================================

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/income",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(incomeData)

            }
        );


        console.log(
            "API STATUS:",
            response.status
        );


        const result =
            await response.json();


        console.log(
            "API RESPONSE:",
            result
        );


        if (!response.ok) {

            alert(
                result.message ||
                "Failed to add income."
            );

            return;
        }


        // =================================================
        // SUCCESS
        // =================================================

        alert(
            "Income Added Successfully!"
        );


        document
            .getElementById("incomeForm")
            .reset();


        loadIncome();


    }

    catch (error) {

        console.error(
            "INCOME API ERROR:",
            error
        );

        alert(
            "Cannot connect to backend. Make sure Flask is running."
        );

    }

}


// =====================================================
// LOAD INCOME
// =====================================================

async function loadIncome() {

    const userEmail =
        localStorage.getItem("userEmail") ||
        localStorage.getItem("email");


    if (!userEmail) {

        console.warn(
            "No user email found."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/income?userEmail=" +
                encodeURIComponent(userEmail)
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " + response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "INCOME FROM DATABASE:",
            data
        );


        updateIncomeSummary(data);

        displayIncome(data);

    }

    catch (error) {

        console.error(
            "LOAD INCOME ERROR:",
            error
        );

    }

}


// =====================================================
// UPDATE SUMMARY
// =====================================================

function updateIncomeSummary(data) {

    if (!Array.isArray(data)) {

        return;
    }


    // =================================================
    // TOTAL INCOME
    // =================================================

    const totalIncome =
        data.reduce(
            (total, item) => {

                return total +
                    Number(item.amount || 0);

            },
            0
        );


    const totalElement =
        document.getElementById(
            "totalIncome"
        );


    if (totalElement) {

        totalElement.textContent =
            formatCurrency(totalIncome);

    }


    // =================================================
    // THIS MONTH
    // =================================================

    const now =
        new Date();


    const currentYear =
        now.getFullYear();


    const currentMonth =
        String(
            now.getMonth() + 1
        ).padStart(2, "0");


    const monthKey =
        `${currentYear}-${currentMonth}`;


    const monthlyIncome =
        data.reduce(
            (total, item) => {

                if (
                    String(item.date)
                        .startsWith(monthKey)
                ) {

                    return total +
                        Number(item.amount || 0);

                }

                return total;

            },
            0
        );


    const monthlyElement =
        document.getElementById(
            "monthlyIncome"
        );


    if (monthlyElement) {

        monthlyElement.textContent =
            formatCurrency(monthlyIncome);

    }


    // =================================================
    // RECURRING INCOME
    // =================================================

    const recurringIncome =
        data.reduce(
            (total, item) => {

                if (item.recurring === true) {

                    return total +
                        Number(item.amount || 0);

                }

                return total;

            },
            0
        );


    const recurringElement =
        document.getElementById(
            "recurringIncome"
        );


    if (recurringElement) {

        recurringElement.textContent =
            formatCurrency(recurringIncome);

    }


    // =================================================
    // MAIN SOURCE
    // =================================================

    const sourceTotals = {};


    data.forEach(item => {

        const source =
            item.source || "Other";


        sourceTotals[source] =
            (
                sourceTotals[source] || 0
            ) +
            Number(item.amount || 0);

    });


    let mainSource = "--";


    let highestAmount = 0;


    Object.entries(sourceTotals)
        .forEach(
            ([source, total]) => {

                if (total > highestAmount) {

                    highestAmount =
                        total;

                    mainSource =
                        source;

                }

            }
        );


    const sourceElement =
        document.getElementById(
            "mainIncomeSource"
        );


    if (sourceElement) {

        sourceElement.textContent =
            mainSource;

    }


    // =================================================
    // COUNT
    // =================================================

    const countElement =
        document.getElementById(
            "incomeCount"
        );


    if (countElement) {

        countElement.textContent =
            `${data.length} Record${data.length === 1 ? "" : "s"}`;

    }

}


// =====================================================
// DISPLAY TRANSACTIONS
// =====================================================

function displayIncome(data) {

    const tableBody =
        document.getElementById(
            "incomeTableBody"
        );


    if (!tableBody) {

        return;
    }


    tableBody.innerHTML = "";


    if (
        !data ||
        data.length === 0
    ) {

        tableBody.innerHTML = `

            <tr class="empty-row">

                <td colspan="6">

                    <div class="empty-state">

                        <i class="fa-solid fa-wallet"></i>

                        <h3>No Income Added</h3>

                        <p>
                            Add your first income transaction
                            to start tracking your earnings.
                        </p>

                    </div>

                </td>

            </tr>

        `;

        return;
    }


    data.forEach(item => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${item.date || ""}
            </td>

            <td>
                ${escapeHtml(
                    item.source || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    item.category || ""
                )}
            </td>

            <td>
                ${formatCurrency(
                    item.amount
                )}
            </td>

            <td>
                ${
                    item.recurring === true
                        ? "Yes"
                        : "No"
                }
            </td>

            <td>

                <button
                    type="button"
                    onclick="deleteIncome('${item._id}')">

                    Delete

                </button>

            </td>

        `;


        tableBody.appendChild(row);

    });

}


// =====================================================
// DELETE INCOME
// =====================================================

async function deleteIncome(id) {

    if (
        !confirm(
            "Are you sure you want to delete this income?"
        )
    ) {

        return;
    }


    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/income/" +
                id,
                {

                    method: "DELETE"

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.message ||
                "Unable to delete income."
            );

            return;
        }


        alert(
            "Income Deleted Successfully!"
        );


        loadIncome();

    }

    catch (error) {

        console.error(
            "DELETE ERROR:",
            error
        );

    }

}


// =====================================================
// CURRENCY
// =====================================================

function formatCurrency(amount) {

    return new Intl.NumberFormat(
        "en-IN",
        {

            style: "currency",

            currency: "INR",

            minimumFractionDigits: 2

        }
    ).format(
        Number(amount) || 0
    );

}


// =====================================================
// HTML SAFETY
// =====================================================

function escapeHtml(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}