# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: playthrough.spec.ts >> Stellar Frontiers Full Playthrough >> Two players can create room, join, and play
- Location: tests\e2e\playthrough.spec.ts:4:3

# Error details

```
Test timeout of 30000ms exceeded.
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - generic [ref=e5]:
      - 'heading "Sector: R5RZ5E" [level=2] [ref=e6]'
      - paragraph [ref=e7]: Round 1 • reinforcement
    - generic [ref=e8]:
      - generic [ref=e9]:
        - paragraph [ref=e10]: Reinforcements
        - heading "3" [level=3] [ref=e11]
      - heading "YOUR TURN" [level=3] [ref=e13]
  - generic [ref=e14]:
    - generic [ref=e15]:
      - img [ref=e17]:
        - generic [ref=e34]:
          - generic [ref=e35] [cursor=pointer]:
            - generic: "1"
            - generic: N1
            - generic: HostCommander
          - generic [ref=e38] [cursor=pointer]:
            - generic: "1"
            - generic: N2
            - generic: HostCommander
          - generic [ref=e41] [cursor=pointer]:
            - generic: "1"
            - generic: N3
            - generic: GuestCommander
          - generic [ref=e44] [cursor=pointer]:
            - generic: "1"
            - generic: I1
            - generic: GuestCommander
          - generic [ref=e47] [cursor=pointer]:
            - generic: "1"
            - generic: I2
            - generic: GuestCommander
          - generic [ref=e50] [cursor=pointer]:
            - generic: "1"
            - generic: I3
            - generic: GuestCommander
          - generic [ref=e53] [cursor=pointer]:
            - generic: "2"
            - generic: C1
            - generic: GuestCommander
          - generic [ref=e56] [cursor=pointer]:
            - generic: "1"
            - generic: C2
            - generic: HostCommander
          - generic [ref=e59] [cursor=pointer]:
            - generic: "1"
            - generic: C3
            - generic: HostCommander
          - generic [ref=e62] [cursor=pointer]:
            - generic: "1"
            - generic: C4
            - generic: GuestCommander
          - generic [ref=e65] [cursor=pointer]:
            - generic: "1"
            - generic: S1
            - generic: HostCommander
          - generic [ref=e68] [cursor=pointer]:
            - generic: "1"
            - generic: S2
            - generic: HostCommander
          - generic [ref=e71] [cursor=pointer]:
            - generic: "1"
            - generic: S3
            - generic: GuestCommander
      - generic [ref=e74]:
        - button "Advance Phase" [ref=e75] [cursor=pointer]
        - button "End Turn" [ref=e76] [cursor=pointer]
    - generic [ref=e77]:
      - heading "Comms Log" [level=3] [ref=e78]
      - generic [ref=e79]:
        - generic [ref=e80]:
          - strong [ref=e81]: "[turn_started]"
          - text: Turn started
        - generic [ref=e82]:
          - strong [ref=e83]: "[match_started]"
          - text: Match started
```