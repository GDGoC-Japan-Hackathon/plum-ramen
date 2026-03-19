import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

const app = initializeApp({
    apiKey: "AIzaSyDiwTbSQTk3ywXbAbtpxZDDkv1SxjtTJ-w",
    authDomain: "gdgoc2026.firebaseapp.com",
    projectId: "gdgoc2026",
});
const auth = getAuth(app);

export function getIdToken() {
    // Firebaseがログイン状態の確認を終えるまで待ってからトークンを返す
    return new Promise((resolve, reject) => {
        onAuthStateChanged(auth, async (user) => {
            if (user) {
                resolve(await user.getIdToken());
            } else {
                reject(new Error("ログインしていません"));
            }
        });
    });
}

export function requireLogin() {
    onAuthStateChanged(auth, (user) => {
        if (!user) {
            window.location.href = "/login";
        }
    })
}