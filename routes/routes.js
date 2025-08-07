const express = require('express');
const User = require('../model/model');
const path = require('path');

const router = express.Router();

// The GET route should serve the registration.html page
router.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, '../registration.html'));
});

// The POST route should handle the form submission
router.post("/", async(req, res) => {
    try {
        const newUser = new User({
            name: req.body.name,
            email: req.body.email,
            password: req.body.password
        });
        await newUser.save();
        // Redirect to a success page or send a success message
        res.send("Registration successful!");
    } catch(err) {
        console.error('Error saving user data', err);
        res.status(500).send('Error saving user data');
    }
});

module.exports = router;