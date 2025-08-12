const express = require('express');
const User = require('../model/model');
const path = require('path');
const bcrypt = require('bcrypt');

const router = express.Router();

// Serve homepage.html
router.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, '../homepage.html'));
});

// Handle user registration
router.post("/", async (req, res) => {
    try {
        const existingUser = await User.findOne({ email: req.body.email });
        if (existingUser) {
            return res.send("User with this email already exists");
        }

        // Hash password before saving
        const hashedPassword = await bcrypt.hash(req.body.password, 10);

        const newUser = new User({
            name: req.body.name,
            email: req.body.email,
            password: hashedPassword
        });

        await newUser.save();
        res.redirect("/home.html");
    } catch (err) {
        console.error('Error saving user data', err);
        res.status(500).send('Error saving user data');
    }
});

// Serve login page
router.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '../login.html'));
});

// Handle user login
router.post('/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).send('User not found');
        }

        // Compare hashed password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(401).send('Invalid credentials');
        }

        res.redirect("/home.html");
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).send('Internal server error');
    }
});

module.exports = router;