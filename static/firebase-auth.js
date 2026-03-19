const firebaseConfig = window.__FIREBASE_CONFIG__ || {};
const sdkVersion = window.__FIREBASE_SDK_VERSION__ || "11.6.0";

const [{ getApp, getApps, initializeApp }, authModule] = await Promise.all([
    import(`https://www.gstatic.com/firebasejs/${sdkVersion}/firebase-app.js`),
    import(`https://www.gstatic.com/firebasejs/${sdkVersion}/firebase-auth.js`),
]);

const {
    getAuth,
    GoogleAuthProvider,
    onAuthStateChanged,
    signInWithPopup,
    signOut,
} = authModule;

function assertFirebaseConfig() {
    const requiredKeys = ["apiKey", "authDomain", "projectId", "appId"];
    const missingKeys = requiredKeys.filter((key) => !firebaseConfig[key]);

    if (missingKeys.length > 0) {
        throw new Error(`Firebase config is missing: ${missingKeys.join(", ")}`);
    }
}

assertFirebaseConfig();

const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
provider.addScope("profile");
provider.addScope("email");

export function waitForAuthState() {
    return new Promise((resolve) => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            unsubscribe();
            resolve(user);
        });
    });
}

export async function signInWithGoogle() {
    return signInWithPopup(auth, provider);
}

export async function signOutUser() {
    await signOut(auth);
}

export async function getIdTokenOrNull(forceRefresh = false) {
    const user = auth.currentUser || await waitForAuthState();
    if (!user) {
        return null;
    }
    return user.getIdToken(forceRefresh);
}

export async function authFetch(input, init = {}) {
    const token = await getIdTokenOrNull();
    const headers = new Headers(init.headers || {});

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    return fetch(input, {
        ...init,
        headers,
    });
}

export async function mountProtectedPage({ authBarId = "auth-bar", redirectTo = "/" } = {}) {
    const user = await waitForAuthState();
    if (!user) {
        window.location.href = redirectTo;
        return null;
    }

    const response = await authFetch("/api/me");
    if (!response.ok) {
        await signOutUser();
        window.location.href = redirectTo;
        return null;
    }

    const profile = await response.json();
    const authBar = document.getElementById(authBarId);
    if (authBar) {
        authBar.innerHTML = "";

        const wrapper = document.createElement("div");
        wrapper.style.display = "flex";
        wrapper.style.justifyContent = "space-between";
        wrapper.style.alignItems = "center";
        wrapper.style.gap = "12px";
        wrapper.style.flexWrap = "wrap";

        const userBlock = document.createElement("div");
        const nameElement = document.createElement("strong");
        nameElement.textContent = profile.name || "Signed in";
        const emailElement = document.createElement("div");
        emailElement.style.fontSize = "0.9rem";
        emailElement.textContent = profile.email || "";

        userBlock.appendChild(nameElement);
        userBlock.appendChild(emailElement);

        const signOutButton = document.createElement("button");
        signOutButton.type = "button";
        signOutButton.textContent = "Sign out";
        signOutButton.addEventListener("click", async () => {
            await signOutUser();
            window.location.href = redirectTo;
        });

        wrapper.appendChild(userBlock);
        wrapper.appendChild(signOutButton);
        authBar.appendChild(wrapper);
    }

    return profile;
}
