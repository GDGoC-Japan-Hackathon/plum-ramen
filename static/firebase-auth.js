import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import { getAuth, signOut, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

const app = initializeApp({
    apiKey: "AIzaSyDiwTbSQTk3ywXbAbtpxZDDkv1SxjtTJ-w",
    authDomain: "gdgoc2026.firebaseapp.com",
    projectId: "gdgoc2026",
});
export const auth = getAuth(app);

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

export async function login() {
    try {
        // googleログイン設定
        const provider = new GoogleAuthProvider();
        // googleログイン開始
        await signInWithPopup(auth, provider);
    } catch (error) {
        // ポップアップを閉じた場合は無視(ユーザーによる操作)、それ以外はアラート
        if (error.code === "auth/popup-closed-by-user") {
            throw new Error("ログインに失敗しました");
        }
    }
}

export async function logout() {
    await signOut(auth);
    window.location.href = "/login";
}

export function requireLogin() {
    onAuthStateChanged(auth, (user) => {
        if (!user) {
            window.location.href = "/login";
        }
    })
}
