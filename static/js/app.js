import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.9.4/firebase-auth.js";
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.9.4/firebase-app.js";
import { getDatabase, ref, set, update, onValue } from "https://www.gstatic.com/firebasejs/9.9.4/firebase-database.js";

const firebaseConfig = {
    apiKey: "AIzaSyDRt6OKLcM23ngVDHi6U6Xc3yQzw0m5_2I",
    authDomain: "edc-website-6f8a9.firebaseapp.com",
    projectId: "edc-website-6f8a9",
    storageBucket: "edc-website-6f8a9.appspot.com",
    messagingSenderId: "968628347543",
    appId: "1:968628347543:web:8ce76d0ef5d90485adffd2",
    databaseURL: "https://edc-website-6f8a9-default-rtdb.asia-southeast1.firebasedatabase.app",
    measurementId: "G-0MYNYP0Q3S"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getDatabase();

getCurrentUser();

function signin() {
    const email = document.getElementById("email").value; //document.getElementById("email").value;
    const password = document.getElementById("password").value; //document.getElementById("password").value;
    console.log(email, password);
    if (!(email == "" || password == "")) {
        signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                alert("Logged In : " + user.uid);
            }).catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                console.log(errorMessage);
            })
    }
}

function cUser() {
    createUserWithEmailAndPassword(auth, "aaa@wasim2.com", "1234567")
        .then((userCredential) => {
            // Signed in 
            const user = userCredential.user;
            let r = ref(db, 'Users/' + user.uid);
            console.log("User Created : " + user.uid);
            console.log(r);
            set(r, {
                "username": "Wasim 2",
                "email": "aaa@wasim2.com",
                "branch": "ai eng"
            });
            alert("Data Uploaded");
            // ...
        })
        .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
        });
}

var uid = "";

function getCurrentUser() {
    onAuthStateChanged(auth, (user) => {
        if (user) {
            // User is signed in, see docs for a list of available properties
            // https://firebase.google.com/docs/reference/js/firebase.User
            uid = user.uid;
            // ...
        } else {
            // User is signed out
            // ...
        }
    });
}

function temp() {

    let r = ref(db, '/Events');
    console.log("User Created : " + uid);
    console.log(r);
    onValue(r, (snapshot) => {
        const data = snapshot.val();
        for (let key in data) {
            console.log("data[key]", data[key]);
            for (let innerKey in data[key]) {
                var obj = {};
                obj[innerKey] = data[key][innerKey];
                console.log("\t", innerKey, obj[innerKey]);
            }
        }
    });

}



// var but = document.getElementById("hello");
// but.addEventListener('click', (e) => {
//     temp();
// })
var sign = document.getElementById("sub");
sign.addEventListener('click', (e) => {
    signin();
})