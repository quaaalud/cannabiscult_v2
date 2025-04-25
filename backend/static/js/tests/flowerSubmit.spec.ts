import * as dotenv from 'dotenv';
dotenv.config();
import { test, expect } from '@playwright/test';
dotenv.config();
test('Flower form: every step advances and final Submit fires POST', async ({ page }) => {
  await page.goto('http://localhost:8000/get-review?strain_selected=Red+Velvet+Runtz+&cultivator_selected=Blue+Arrow+');

  await page.fill('#loginModalEmail', process.env.TEST_USER!);
  await page.fill('#loginModalPassword', process.env.TEST_PASS!);
  await page.click('button[name="login-submit"]');
  await page.waitForTimeout(1000);
  await page.click('#startReviewBtn');
  await page.waitForTimeout(1000);
  await page.click('#nextBtn');
  await page.waitForTimeout(1000);
  const steps = [
    { type: 'rating', name: 'appearance_rating' },
    { type: 'text',   name: 'appearance_explanation' },
    { type: 'rating', name: 'smell_rating' },
    { type: 'text',   name: 'smell_explanation' },
    { type: 'rating', name: 'freshness_rating' },
    { type: 'text',   name: 'freshness_explanation' },
    { type: 'rating', name: 'flavor_rating' },
    { type: 'text',   name: 'flavor_explanation' },
    { type: 'rating', name: 'harshness_rating' },
    { type: 'text',   name: 'harshness_explanation' },
    { type: 'rating', name: 'effects_rating' },
    { type: 'multiselect', name: 'effects_explanation' },
  ];

  // 5) Intercept the POST so we can assert it later
  let sawSubmitRequest = false;
  page.on('request', req => {
    if (req.url().endsWith('/flowers/ranking') && req.method() === 'POST') {
      sawSubmitRequest = true;
    }
  });
  await page.waitForTimeout(200);
  // 6) Loop through steps
  for (const step of steps) {
    if (step.type === 'rating') {
      // pick a safe mid value
      await page.click(`label[for="${step.name}3"]`);
    }
    else if (step.type === 'text') {
      // fill the explanation input
      await page.fill(`#${step.name}`, `This is a sample explanation for ${step.name}`);
    }
    else if (step.type === 'multiselect') {
      // choose two options from the multi-select
      await page.selectOption(
        `#${step.name}`,
        ['sedative', 'relaxing']  // any two from the <option> list
      );
    }
    await page.click('#nextBtn');
    await page.waitForTimeout(200);
  };
  await page.fill('#pack_code', 'TESTCP1');
  await page.click('#nextBtn');
  await page.click('#nextBtn');

  expect(sawSubmitRequest).toBe(true);
});
