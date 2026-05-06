const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function capture() {
    const artifactDir = 'C:\\Users\\lenovo\\.gemini\\antigravity\\brain\\d17c90f0-0004-4435-959e-9081efe093c3';
    if (!fs.existsSync(artifactDir)) fs.mkdirSync(artifactDir, { recursive: true });

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        locale: 'fr-FR',
        viewport: { width: 1440, height: 900 }
    });
    const page = await context.newPage();

    console.log("Navigating to dashboard...");
    await page.goto('http://localhost:5177', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000); // Let animations run

    const frDashPath = path.join(artifactDir, `react_dashboard_fr_${Date.now()}.png`);
    await page.screenshot({ path: frDashPath });
    console.log(`Saved FR dashboard: ${frDashPath}`);

    console.log("Switching Language to EN...");
    // Find language toggle button
    try {
        await page.locator('button:has-text("FR")').click();
        await page.waitForTimeout(1000);
        const enDashPath = path.join(artifactDir, `react_dashboard_en_${Date.now()}.png`);
        await page.screenshot({ path: enDashPath });
        console.log(`Saved EN dashboard: ${enDashPath}`);
    } catch (e) {
        console.error("Could not find language toggle.", e);
    }

    // Open the student modal
    console.log("Opening Student Modal...");
    try {
        const firstRow = page.locator('tbody tr').first();
        await firstRow.click();
        await page.waitForTimeout(1500); // Wait for modal load
        const modalPath = path.join(artifactDir, `react_student_modal_fr_${Date.now()}.png`);
        await page.screenshot({ path: modalPath });
        console.log(`Saved Student Modal: ${modalPath}`);
    } catch (e) {
        console.error("Could not open student modal.", e);
    }

    await browser.close();
    console.log("Capture complete.");
}

capture().catch(console.error);
