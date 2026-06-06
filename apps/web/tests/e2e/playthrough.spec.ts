import { test, expect } from '@playwright/test';

test.describe('Stellar Frontiers Full Playthrough', () => {
  test('Two players can create room, join, and play', async ({ browser }) => {
    // We need 2 separate browser contexts to simulate 2 distinct players
    const p1Context = await browser.newContext();
    const p2Context = await browser.newContext();

    const p1Page = await p1Context.newPage();
    const p2Page = await p2Context.newPage();

    p1Page.on('console', msg => console.log('P1 Console:', msg.type(), msg.text()));
    p1Page.on('pageerror', err => console.log('P1 PageError:', err.message));
    p2Page.on('console', msg => console.log('P2 Console:', msg.type(), msg.text()));
    p2Page.on('pageerror', err => console.log('P2 PageError:', err.message));

    // Player 1 - Create Room
    await p1Page.goto('/');
    await p1Page.fill('input[placeholder="Enter your alias"]', 'HostCommander');
    await p1Page.click('button:has-text("Form New Fleet")');

    // Wait for room to be created and check for Sector header
    await expect(p1Page.locator('h1', { hasText: 'Sector' })).toBeVisible();
    
    // Extract Room Code
    const sectorText = await p1Page.locator('h1').innerText();
    const roomCode = sectorText.replace('Sector ', '').trim();
    expect(roomCode).toHaveLength(6);

    // Player 2 - Join Room
    await p2Page.goto('/');
    await p2Page.fill('input[placeholder="Enter your alias"]', 'GuestCommander');
    await p2Page.fill('input[placeholder="Room Code"]', roomCode);
    await p2Page.click('button:has-text("Join")');

    // Wait for Player 2 to join
    await expect(p2Page.locator('h1', { hasText: `Sector ${roomCode}` })).toBeVisible();

    // Allow time for WebSocket connection to establish for Player 2
    await p1Page.waitForTimeout(1000);

    // Player 1 - Start Match
    await p1Page.click('button:has-text("Initiate Jump")');

    // Both should see "Round 1" and the SVG Map
    await expect(p1Page.locator('text=Round 1')).toBeVisible();
    await expect(p2Page.locator('text=Round 1')).toBeVisible();

    // Check that SVG map rendered by looking for nodes
    await expect(p1Page.locator('.map-node')).toHaveCount(13, { timeout: 10000 });

    // Turn 1 is Player 1 (deterministic alphabetical order: GuestCommander vs HostCommander)
    // GuestCommander is 'G', HostCommander is 'H'. GuestCommander is first.
    // Let's explicitly check who has the YOUR TURN text
    let p1Turn = false;
    try {
      await p1Page.locator('text=YOUR TURN').waitFor({ timeout: 2000 });
      p1Turn = true;
    } catch {
      p1Turn = false;
    }
    
    const currentPlayerPage = p1Turn ? p1Page : p2Page;
    const opponentPage = p1Turn ? p2Page : p1Page;

    // Wait for it to be visible on the current player page
    await expect(currentPlayerPage.locator('text=YOUR TURN')).toBeVisible();

    // Check reinforcement phase
    await expect(currentPlayerPage.locator('text=Round 1 • reinforcement')).toBeVisible();
    
    // In default layout, N1 is often owned by someone.
    // If Guest (first alphabetically) is playing, they own N1 and N3. Wait, alphabetical order: GuestCommander, HostCommander.
    // players[0] gets N1, N3. players[1] gets N2, N4.
    // So Guest gets N1. Host gets N2.
    // Let's just click N1 if Guest, N2 if Host.
    const myNode = p1Turn ? 'N1' : 'N2';
    
    await currentPlayerPage.locator('g.map-node').filter({ hasText: new RegExp(`^${myNode}$`) }).click({ force: true });
    
    // Expect ActionModal to appear
    await expect(currentPlayerPage.locator('.modal-content')).toBeVisible();
    await expect(currentPlayerPage.locator('text=Deploy Fleet')).toBeVisible();
    
    // Deploy 1 fleet
    await currentPlayerPage.fill('input[type="number"]', '1');
    await currentPlayerPage.click('button:has-text("Execute")');

    // Modal closes
    await expect(currentPlayerPage.locator('.modal-content')).not.toBeVisible();

    // Advance Phase
    await currentPlayerPage.click('button:has-text("Advance Phase")');
    await expect(currentPlayerPage.locator('text=Round 1 • attack')).toBeVisible();
    await expect(opponentPage.locator('text=Round 1 • attack')).toBeVisible();

    // Attack
    // N1 is adjacent to N2.
    const targetNode = p1Turn ? 'N2' : 'N1';
    
    await currentPlayerPage.locator('g.map-node').filter({ hasText: new RegExp(`^${myNode}$`) }).click({ force: true }); // Source
    await currentPlayerPage.locator('g.map-node').filter({ hasText: new RegExp(`^${targetNode}$`) }).click({ force: true }); // Target

    // Expect ActionModal for Attack
    await expect(currentPlayerPage.locator('.modal-content')).toBeVisible();
    await expect(currentPlayerPage.locator('text=Initiate Attack')).toBeVisible();
    
    // Execute Attack
    await currentPlayerPage.click('button:has-text("Execute")');
    await expect(currentPlayerPage.locator('.modal-content')).not.toBeVisible();

    // Advance Phase again
    await currentPlayerPage.click('button:has-text("Advance Phase")');
    await expect(currentPlayerPage.locator('text=Round 1 • movement')).toBeVisible();

    // End Turn
    await currentPlayerPage.click('button:has-text("End Turn")');
    
    // Check that turn passed to the other player
    await expect(opponentPage.locator('text=YOUR TURN')).toBeVisible();
    
    await p1Context.close();
    await p2Context.close();
  });
});
