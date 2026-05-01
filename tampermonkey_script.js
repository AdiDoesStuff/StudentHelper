// ==UserScript==
// @name         Evalify to AEGIS-MIND Exporter (v1.3)
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  Robust extraction including coding answers and variable marks
// @author       AdityaVineeth
// @match        http://v1.evalify.amritanet.edu/student/quiz/result/*
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    const BUTTON_ID = 'aegis-mind-export-btn';

    const createButton = () => {
        if (document.getElementById(BUTTON_ID)) return;

        const btn = document.createElement('button');
        btn.id = BUTTON_ID;
        btn.innerHTML = 'Copy JSON for AEGIS-MIND';
        btn.style = `
            position: fixed; top: 100px; right: 20px; z-index: 10000;
            padding: 12px 24px; background-color: #6366f1; color: white;
            border: 2px solid white; border-radius: 8px; cursor: pointer;
            font-weight: bold; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        `;
       
        btn.onmouseover = () => btn.style.transform = 'scale(1.05)';
        btn.onmouseout = () => btn.style.transform = 'scale(1)';
        btn.onclick = exportData;
       
        document.body.appendChild(btn);
    };

    const exportData = () => {
        const questionBlocks = document.querySelectorAll('div.space-y-4.p-4.rounded-lg.border');
       
        if (questionBlocks.length === 0) {
            alert("No quiz questions detected.");
            return;
        }

        const extractedData = [];

        questionBlocks.forEach((block, index) => {
            // 1. Capture question text
            const questionContainer = block.querySelector('.prose');
            const questionText = questionContainer ? questionContainer.innerText.trim() : "Text not found";
           
            // 2. Dynamic Outcome Logic (Matches awarded marks vs total marks)
            const marksMatch = block.innerText.match(/(\d+)\s*\/\s*(\d+)\s*marks/);
            const outcome = (marksMatch && marksMatch[1] === marksMatch[2]) ? 1 : 0;

            // 3. Extract Options & Correct Answer
            const optionElements = block.querySelectorAll('.grid-cols-1 .p-4');
            let options = [];
            let correctAnswer = "";

            if (optionElements.length > 0) {
                // MCQ Handling
                optionElements.forEach(opt => {
                    const letter = opt.querySelector('span')?.innerText.replace('.', '').trim() || "";
                    const text = opt.querySelector('.prose span')?.innerText.trim() || "";
                    options.push(`${letter}) ${text}`);
                   
                    if (opt.className.includes('border-green-500') || opt.querySelector('.lucide-circle-check-big')) {
                        correctAnswer = letter;
                    }
                });
            } else {
                // Coding / Open-ended Handling
                const yourAnswerPre = block.querySelector('pre');
                if (yourAnswerPre) {
                    correctAnswer = yourAnswerPre.innerText.trim();
                } else {
                    const expectedBox = block.querySelector('div.bg-green-50');
                    correctAnswer = expectedBox ? expectedBox.innerText.trim() : "Manual Review Required";
                }
            }

            extractedData.push({
                "student_id": 1,
                "test_id": window.location.pathname.split('/').pop(),
                "topic_tag": null,
                "question_id": index + 1,
                "question_text": questionText,
                "options": options,
                "correct_answer": correctAnswer,
                "outcome": outcome,
                "time_spent_seconds": null,
                "difficulty_level": null,
                "test_sequence_number": index + 1,
                "time_of_day": null,
                "sleep_hours": null,
                "stress_level": null
            });
        });

        GM_setClipboard(JSON.stringify(extractedData, null, 2));
        alert(`Exported ${extractedData.length} questions. Coding answers and variable marks are now included!`);
    };

    const observer = new MutationObserver(() => {
        if (!document.getElementById(BUTTON_ID)) createButton();
    });

    observer.observe(document.body, { childList: true, subtree: true });
    createButton();
})();
