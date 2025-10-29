# Video Demo Script

**Duration**: 3-5 minutes  
**Format**: Screen recording with voiceover

---

## Scene 1: Introduction (30 seconds)

**Screen**: Show project README or title slide

**Script**:
> "Today I'll demonstrate StatSQLi, a tool that makes time-based blind SQL injection 10 to 20 times faster than existing tools. Time-based injection is notoriously slow because you can't see results directly - you only infer data by measuring server response times. StatSQLi solves this using statistics, binary search, and adaptive delays."

**Action**: Fade to terminal/demo screen

---

## Scene 2: Setup (30 seconds)

**Screen**: Terminal showing installation

**Script**:
> "First, let's verify StatSQLi is installed and start our vulnerable lab application. The lab app has intentional SQL injection vulnerabilities for testing."

**Action**:
```bash
# Show installation
pip install -e .

# Start lab app
cd lab
python app.py
# Show it's running on http://127.0.0.1:5000
```

**Visual**: Split screen or quick cut between setup steps

---

## Scene 3: The Problem (45 seconds)

**Screen**: Terminal showing slow extraction method (optional - simulated or skipped)

**Script**:
> "Traditional tools like SQLMap use linear search - they test each of the 95 possible ASCII characters one by one. For a 20-character string, that's almost 2,000 queries. With 2-second delays, that's over an hour. And network noise causes false positives, making it unreliable."

**Visual**: 
- Show example of slow linear extraction (can be simulated/edited)
- Highlight the inefficiency

---

## Scene 4: StatSQLi Solution - Statistical Analysis (60 seconds)

**Screen**: Running StatSQLi with detailed output

**Script**:
> "StatSQLi starts by establishing a statistical baseline. It measures multiple requests without delays to understand the natural network noise. Then, when testing conditions, it uses Welch's t-test - a statistical method - to determine if a timing difference is real or just noise. This reduces false positives by about 90 percent."

**Action**:
```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND 1=1" \
    --table users \
    --column username
```

**Visual**: 
- Show baseline establishment messages
- Highlight "statistical analysis" output
- Show p-values or confidence messages

---

## Scene 5: Binary Search Speedup (60 seconds)

**Screen**: Extraction in progress

**Script**:
> "Instead of checking all 95 characters linearly, StatSQLi uses binary search. It asks 'Is the character greater than or equal to 64?' If yes, it checks the upper half. If no, the lower half. This finds each character in about 7 queries instead of 95 - that's over 13 times fewer queries."

**Action**:
- Show extraction progress
- Highlight how quickly characters are found
- Point out the binary search approach

**Visual**: 
- Progress bar or character-by-character output
- Maybe show a quick diagram of binary search (split screen)

---

## Scene 6: Adaptive Delays (45 seconds)

**Screen**: Delay detection output

**Script**:
> "Before extraction, StatSQLi automatically detects the optimal delay. It tests different delay values and picks the smallest one that's reliably detectable above network noise. This means it works well on both fast local networks and slower internet connections."

**Action**:
- Show delay detection phase
- Highlight adaptive tuning messages

---

## Scene 7: Parallel Extraction & Results (60 seconds)

**Screen**: Fast extraction with parallel mode

**Script**:
> "We can also enable parallel extraction to extract multiple characters at once. Let's see the full extraction in action."

**Action**:
```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND 1=1" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1" \
    --parallel
```

**Visual**:
- Show extraction progress
- Time elapsed counter
- Final result: extracted username/password

**Script (continued)**:
> "As you can see, StatSQLi extracted the username in about 45 seconds. Compare that to SQLMap which takes 7 minutes, or manual tools which take over an hour. That's a 10 to 20 times speedup while actually being more reliable thanks to statistical validation."

---

## Scene 8: Benchmark Results (45 seconds)

**Screen**: Show benchmark charts/results

**Script**:
> "Here are benchmark results from multiple test runs. StatSQLi consistently outperforms SQLMap by an order of magnitude, while maintaining 100 percent success rate with much lower false positives."

**Visual**:
- Show comparison charts (from benchmarks/generate_charts.py)
- Bar chart: StatSQLi vs SQLMap vs Manual
- Speedup factors highlighted

---

## Scene 9: Conclusion (30 seconds)

**Screen**: Summary slide or final output

**Script**:
> "StatSQLi demonstrates that applying statistics and smart algorithms to security tools can achieve dramatic improvements. By combining binary search, statistical validation, and adaptive tuning, we've made time-based blind SQL injection practical for security testing. Thank you for watching."

**Visual**:
- Key metrics: 10-20× speedup, 90% fewer false positives
- GitHub/repo link (if applicable)
- Credits

---

## Production Notes

### Recording Tips:
1. **Clear Terminal**: Use clear/clean terminal themes for better visibility
2. **Zoom**: Zoom in on terminal during demonstrations
3. **Pacing**: Don't rush - extraction takes time, that's okay!
4. **Annotations**: Add text overlays for key concepts (e.g., "Binary Search", "Statistical Test")
5. **Transitions**: Smooth transitions between scenes

### Editing Tips:
1. **Speed Up**: You can speed up the extraction progress (1.5x-2x) if it's too slow
2. **Highlights**: Add highlights/circles to emphasize key output
3. **Subtitles**: Consider adding subtitles for clarity
4. **Background Music**: Optional, but keep it subtle if used

### Software Needed:
- Screen recording: OBS, QuickTime (macOS), ScreenRec (Windows), or similar
- Video editing: iMovie, Premiere, DaVinci Resolve, or similar
- Terminal: iTerm2 (macOS), Terminal.app, or Windows Terminal

### Time Estimates:
- **Setup/Demo Recording**: 10-15 minutes (allow for retakes)
- **Editing**: 1-2 hours
- **Final Video**: 3-5 minutes

---

## Alternative: Shorter Demo (2 minutes)

**Quick Version**:
1. Introduction (15s)
2. Show the problem - traditional tool is slow (20s)
3. Run StatSQLi with parallel mode (60s)
4. Show results and speedup (20s)
5. Conclusion (5s)

Focus on the speed difference and reliability gains.

