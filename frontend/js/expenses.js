// ==========================================
// SMARTSPEND AI
// expenses.js
// ==========================================

const API = "http://127.0.0.1:5000/api";

// ==========================================
// USER
// ==========================================

const userEmail = localStorage.getItem("userEmail");

if (!userEmail) {

    window.location.href = "login.html";

}

// ==========================================
// ADD EXPENSE MODAL
// ==========================================

const expenseModal = document.getElementById("expenseModal");

const openExpenseModal = document.getElementById("openExpenseModal");

const emptyAddExpense = document.getElementById("emptyAddExpense");

const closeModal = document.getElementById("closeModal");

const cancelExpense = document.getElementById("cancelExpense");

// ==========================================
// IMPORT STATEMENT MODAL
// ==========================================

const statementModal = document.getElementById("statementModal");

const uploadStatementBtn = document.getElementById("uploadStatementBtn");

const closeStatementModal = document.getElementById("closeStatementModal");

const cancelStatement = document.getElementById("cancelStatement");

// ==========================================
// OPEN ADD EXPENSE
// ==========================================

function openExpense(){

    expenseModal.style.display = "flex";

    document.body.style.overflow = "hidden";

}

if(openExpenseModal){

    openExpenseModal.onclick = openExpense;

}

if(emptyAddExpense){

    emptyAddExpense.onclick = openExpense;

}

// ==========================================
// CLOSE ADD EXPENSE
// ==========================================

function closeExpense(){

    expenseModal.style.display = "none";

    document.body.style.overflow = "auto";

}

if(closeModal){

    closeModal.onclick = closeExpense;

}

if(cancelExpense){

    cancelExpense.onclick = closeExpense;

}

// ==========================================
// OPEN IMPORT MODAL
// ==========================================

function openStatement(){

    statementModal.style.display = "flex";

    document.body.style.overflow = "hidden";

}

if(uploadStatementBtn){

    uploadStatementBtn.onclick = openStatement;

}

// ==========================================
// CLOSE IMPORT MODAL
// ==========================================

function closeStatement(){

    statementModal.style.display = "none";

    document.body.style.overflow = "auto";

}

if(closeStatementModal){

    closeStatementModal.onclick = closeStatement;

}

if(cancelStatement){

    cancelStatement.onclick = closeStatement;

}

// ==========================================
// CLICK OUTSIDE TO CLOSE
// ==========================================

window.onclick = function(event){

    if(event.target === expenseModal){

        closeExpense();

    }

    if(event.target === statementModal){

        closeStatement();

    }

};
// ==========================================
// ADD EXPENSE
// ==========================================

const expenseForm = document.getElementById("expenseForm");

if (expenseForm) {

    expenseForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const expense = {

            title: document.getElementById("expenseTitle").value.trim(),

            category: document.getElementById("expenseCategory").value,

            amount: document.getElementById("expenseAmount").value,

            payment: document.getElementById("payment").value,

            date: document.getElementById("expenseDate").value,

            time: document.getElementById("expenseTime").value,

            transactionType: document.getElementById("transactionType").value,

            source: document.getElementById("expenseSource").value,

            description: document.getElementById("description").value.trim(),

            notes: document.getElementById("notes").value.trim(),

            tags: document.getElementById("tags").value.trim(),

            location: document.getElementById("location").value.trim(),

            userEmail: userEmail

        };

        if (

            expense.title === "" ||

            expense.amount === "" ||

            expense.date === ""

        ) {

            alert("Please fill all required fields.");

            return;

        }

        try {

            let url = API + "/expenses";

let method = "POST";

if(expenseForm.dataset.editId){

    url = API + "/expenses/" + expenseForm.dataset.editId;

    method = "PUT";

}

const response = await fetch(url,{

    method:method,

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(expense)

            });

            const result = await response.json();

if (response.ok) {

    alert(result.message);

    expenseForm.reset();

    delete expenseForm.dataset.editId;

    document.getElementById("expenseSource").value = "Manual";

    closeExpense();

    loadExpenses();

} else {

    alert(result.message);

}

        }

        catch (error) {

            console.error(error);

            alert("Unable to connect to the server.");

        }

    });

}
// ==========================================
// LOAD EXPENSES
// ==========================================

async function loadExpenses(month = null) {

    try {

        let url =
    API +
    "/expenses?userEmail=" +
    encodeURIComponent(userEmail);

if (month) {

    url +=
        "&month=" +
        encodeURIComponent(month);

}

const response = await fetch(url);

        const expenses = await response.json();

        const tbody = document.getElementById("expenseTableBody");

        const expenseCount = document.getElementById("expenseCount");

        tbody.innerHTML = "";

        // ===============================
        // EMPTY STATE
        // ===============================

        if (!expenses.length) {

            tbody.innerHTML = `

            <tr>

                <td colspan="8">

                    <div class="empty-state">

                        <i class="fa-solid fa-wallet"></i>

                        <h3>No Expenses Available</h3>

                        <p>

                            Add a manual expense or import a statement.

                        </p>

                        <button
                            id="emptyAddExpense"
                            class="btn-primary">

                            <i class="fa-solid fa-plus"></i>

                            Add First Expense

                        </button>

                    </div>

                </td>

            </tr>

            `;

            expenseCount.innerText = "0 Records";

            updateSummary([]);

            document
                .getElementById("emptyAddExpense")
                .onclick = openExpense;

            return;

        }

        expenseCount.innerText =

            expenses.length + " Records";

        expenses.forEach(item => {

            tbody.innerHTML += `

            <tr>

                <td>${item.date}</td>

                <td>${item.title}</td>

                <td>

                    <span class="category-badge">

                        ${item.category}

                    </span>

                </td>

                <td>${item.payment || "--"}</td>

                <td>

                    ₹${Number(item.amount).toFixed(2)}

                </td>

                <td>

                    ${item.source || "Manual"}

                </td>

                <td>

                    <span class="status paid">

                        Added

                    </span>

                </td>

                <td>

                    <div class="action-buttons">

                        <button

                            class="edit-btn"

                            onclick="editExpense('${item._id}')">

                            <i class="fa-solid fa-pen"></i>

                        </button>

                        <button

                            class="delete-btn"

                            onclick="deleteExpense('${item._id}')">

                            <i class="fa-solid fa-trash"></i>

                        </button>

                    </div>

                </td>

            </tr>

            `;

        });

        updateSummary(expenses);

    }

    catch (error) {

        console.error(error);

    }

}
// ==========================================
// UPDATE SUMMARY
// ==========================================

function updateSummary(expenses){

    let total = 0;

    let categoryMap = {};

    let paymentMap = {};

    expenses.forEach(exp => {

        total += Number(exp.amount);

        categoryMap[exp.category] =

            (categoryMap[exp.category] || 0) + Number(exp.amount);

        paymentMap[exp.payment] =

            (paymentMap[exp.payment] || 0) + 1;

    });

    document.getElementById("totalExpense").innerText =

        "₹" + total.toFixed(2);

    document.getElementById("totalTransactions").innerText =

        expenses.length;

    let topCategory = "--";

    let topAmount = 0;

    for(const cat in categoryMap){

        if(categoryMap[cat] > topAmount){

            topAmount = categoryMap[cat];

            topCategory = cat;

        }

    }

    document.getElementById("topCategory").innerText =

        topCategory;

    let topPayment = "--";

    let paymentCount = 0;

    for(const pay in paymentMap){

        if(paymentMap[pay] > paymentCount){

            paymentCount = paymentMap[pay];

            topPayment = pay;

        }

    }

    document.getElementById("topPayment").innerText =

        topPayment;

}
// ==========================================
// PAGE LOAD
// ==========================================

const expenseMonth =
    document.getElementById("expenseMonth");

function getCurrentMonth() {

    const today = new Date();

    const year =
        today.getFullYear();

    const month =
        String(
            today.getMonth() + 1
        ).padStart(2, "0");

    return `${year}-${month}`;
}


if (expenseMonth) {

    expenseMonth.value =
        getCurrentMonth();

    loadExpenses(
        expenseMonth.value
    );

    expenseMonth.addEventListener(
        "change",
        function () {

            loadExpenses(
                this.value
            );

        }
    );

}
// ==========================================
// SEARCH & FILTERS
// ==========================================

const searchExpense = document.getElementById("searchExpense");

const merchantSearch = document.getElementById("merchantSearch");

const filterCategory = document.getElementById("filterCategory");

const filterPayment = document.getElementById("filterPayment");

// ==========================================
// FILTER TABLE
// ==========================================

function filterExpenses(){

    const search1 = searchExpense.value.toLowerCase();

    const search2 = merchantSearch.value.toLowerCase();

    const category = filterCategory.value;

    const payment = filterPayment.value;

    const rows = document.querySelectorAll("#expenseTableBody tr");

    rows.forEach(row=>{

        if(row.querySelector(".empty-state")) return;

        const merchant = row.cells[1].innerText.toLowerCase();

        const cat = row.cells[2].innerText.trim();

        const pay = row.cells[3].innerText.trim();

        const visible =

            merchant.includes(search1) &&

            merchant.includes(search2) &&

            (category==="" || cat===category) &&

            (payment==="" || pay===payment);

        row.style.display = visible ? "" : "none";

    });

}

// ==========================================
// EVENTS
// ==========================================

if(searchExpense){

    searchExpense.addEventListener("keyup",filterExpenses);

}

if(merchantSearch){

    merchantSearch.addEventListener("keyup",filterExpenses);

}

if(filterCategory){

    filterCategory.addEventListener("change",filterExpenses);

}

if(filterPayment){

    filterPayment.addEventListener("change",filterExpenses);

}
// ==========================================
// DELETE EXPENSE
// ==========================================

async function deleteExpense(id){

    const confirmDelete = confirm("Are you sure you want to delete this expense?");

    if(!confirmDelete){

        return;

    }

    try{

        const response = await fetch(

            API + "/expenses/" + id,

            {

                method:"DELETE"

            }

        );

        const result = await response.json();

        alert(result.message);

        loadExpenses();

    }

    catch(error){

        console.error(error);

        alert("Unable to delete expense.");

    }

}
// ==========================================
// EDIT EXPENSE
// ==========================================

async function editExpense(id){

    try{

        const response = await fetch(

            API + "/expenses?userEmail=" +

            encodeURIComponent(userEmail)

        );

        const expenses = await response.json();

        const expense = expenses.find(item => item._id === id);

        if(!expense){

            alert("Expense not found.");

            return;

        }

        openExpense();

        document.getElementById("expenseTitle").value = expense.title;

        document.getElementById("expenseAmount").value = expense.amount;

        document.getElementById("expenseCategory").value = expense.category;

        document.getElementById("payment").value = expense.payment || "Cash";

        document.getElementById("expenseDate").value = expense.date;

        document.getElementById("expenseTime").value = expense.time || "";

        document.getElementById("transactionType").value =

            expense.transactionType || "Personal";

        document.getElementById("description").value =

            expense.description || "";

        document.getElementById("notes").value =

            expense.notes || "";

        document.getElementById("tags").value =

            expense.tags || "";

        document.getElementById("location").value =

            expense.location || "";

        expenseForm.dataset.editId = id;

    }

    catch(error){

        console.error(error);

    }

}
// ==========================================
// EXPORT PDF
// ==========================================

const exportPdfBtn = document.getElementById("exportPdf");

if (exportPdfBtn) {

    exportPdfBtn.addEventListener("click", exportPDF);

}

async function exportPDF() {

    try {

        const response = await fetch(

            API + "/expenses?userEmail=" +

            encodeURIComponent(userEmail)

        );

        const expenses = await response.json();

        if (expenses.length === 0) {

            alert("No expenses available.");

            return;

        }

        const { jsPDF } = window.jspdf;

        const doc = new jsPDF();

        // =============================
        // TITLE
        // =============================

        doc.setFontSize(22);

        doc.setTextColor(37,99,235);

        doc.text("SmartSpend AI", 14, 18);

        doc.setFontSize(15);

        doc.setTextColor(60);

        doc.text("Expense Report", 14, 28);

        // =============================
        // USER
        // =============================

        doc.setFontSize(11);

        doc.text("User : " + userEmail, 14, 40);

        doc.text(

            "Generated : " +

            new Date().toLocaleString(),

            14,

            48

        );

        // =============================
        // TOTAL
        // =============================

        let total = 0;

        expenses.forEach(exp => {

            total += Number(exp.amount);

        });

        doc.setFontSize(13);

        doc.text(

            "Total Expense : ₹" +

            total.toFixed(2),

            14,

            60

        );

        // =============================
        // TABLE
        // =============================

        const rows = [];

        expenses.forEach(exp => {

            rows.push([

                exp.date,

                exp.title,

                exp.category,

                exp.payment || "--",

                "₹" + Number(exp.amount).toFixed(2),

                exp.source || "Manual"

            ]);

        });

        doc.autoTable({

            startY:70,

            head:[

                [

                    "Date",

                    "Merchant",

                    "Category",

                    "Payment",

                    "Amount",

                    "Source"

                ]

            ],

            body:rows,

            theme:"grid",

            headStyles:{

                fillColor:[37,99,235]

            }

        });

        // =============================
        // FOOTER
        // =============================

        const pageHeight = doc.internal.pageSize.height;

        doc.setFontSize(10);

        doc.setTextColor(120);

        doc.text(

            "Generated by SmartSpend AI",

            14,

            pageHeight - 10

        );

        doc.save("SmartSpend_Expense_Report.pdf");

    }

    catch(error){

        console.error(error);

        alert("Unable to generate PDF.");

    }

}
// ==========================================
// STATEMENT UPLOAD
// ==========================================

const statementForm = document.getElementById("statementForm");

if (statementForm) {

    statementForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        console.log("Statement form submitted");

        const fileInput =
            document.getElementById("statementFile");

        const passwordInput =
            document.getElementById("statementPassword");

        const file = fileInput.files[0];

        const password = passwordInput.value;

        const userEmail =
            localStorage.getItem("userEmail");

        // -------------------------------
        // CHECK USER
        // -------------------------------

        if (!userEmail) {

            alert("Please login first.");

            return;

        }

        // -------------------------------
        // CHECK FILE
        // -------------------------------

        if (!file) {

            alert("Please select a PDF statement.");

            return;

        }

        // -------------------------------
        // CHECK PDF
        // -------------------------------

        if (!file.name.toLowerCase().endsWith(".pdf")) {

            alert("Please select a PDF file.");

            return;

        }

        // -------------------------------
        // CREATE FORM DATA
        // -------------------------------

        const formData = new FormData();

        formData.append("file", file);

        formData.append("password", password);

        formData.append("userEmail", userEmail);

        try {

            alert("Uploading statement...");

            const response = await fetch(
                API + "/expenses/upload-statement",
                {
                    method: "POST",
                    body: formData
                }
            );

            const result = await response.json();

            console.log("Statement response:", result);

            // -------------------------------
            // ERROR
            // -------------------------------

            if (!response.ok) {

                alert(
                    result.message ||
                    "Unable to process statement."
                );

                return;

            }

            // -------------------------------
            // SUCCESS
            // -------------------------------

            alert(
                "PDF uploaded successfully.\n\n" +
                "The statement was read successfully."
            );

            console.log(
                "Extracted text:",
                result.preview
            );

            statementForm.reset();
            await loadExpenses();
closeStatement();
        }

        catch (error) {

            console.error(
                "UPLOAD ERROR:",
                error
            );

            alert(
                "Unable to connect to backend.\n\n" +
                "Please make sure Flask is running."
            );

        }

    });

}