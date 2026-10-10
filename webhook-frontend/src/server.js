const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// Simulated frontend form endpoint
app.post('/api/submit-lead', async (req, res) => {
    const leadData = req.body;

    try {
        console.log('New lead captured:', leadData);

        // Forward lead data to n8n Webhook Trigger URL
        const n8nWebhookUrl = process.env.N8N_WEBHOOK_URL;
        const response = await axios.post(n8nWebhookUrl, leadData);

        res.status(200).json({
            success: true,
            message: 'Lead captured and forwarded to orchestration pipeline successfully.',
            orchestrationResponse: response.data
        });
    } catch (error) {
        console.error('Error forwarding lead to n8n:', error.message);
        res.status(500).json({ success: false, error: 'Failed to process lead.' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Lead capture server running on port ${PORT}`);
});