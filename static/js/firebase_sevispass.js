import { initializeApp } from "firebase/app";
import {
    getAuth,
    RecaptchaVerifier,
    signInWithPhoneNumber
} from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyABSoTTyyK2QHfUhaCycI2SI-KHaq97508",
    authDomain: "blueshield-sevispass.firebaseapp.com",
    projectId: "blueshield-sevispass",
    storageBucket: "blueshield-sevispass.firebasestorage.app",
    messagingSenderId: "679764318085",
    appId: "1:679764318085:web:ecb2afda5fa9f8f58456ec"
};

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);