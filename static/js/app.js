document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const planForm = document.getElementById('planForm');
    const formCard = document.getElementById('formCard');
    const loadingCard = document.getElementById('loadingCard');
    const loadingStatusText = document.getElementById('loadingStatusText');
    const resultContainer = document.getElementById('resultContainer');
    const destinationInput = document.getElementById('destination');
    const chipBtns = document.querySelectorAll('.chip-btn');
    const styleCards = document.querySelectorAll('.style-card');
    
    // Result Elements
    const resTitle = document.getElementById('resTitle');
    const resSummary = document.getElementById('resSummary');
    const resDestination = document.getElementById('resDestination');
    const resDuration = document.getElementById('resDuration');
    const resBudget = document.getElementById('resBudget');
    const dayTabs = document.getElementById('dayTabs');
    const dayTabsContent = document.getElementById('dayTabsContent');
    const resPackingList = document.getElementById('resPackingList');
    const resTravelTips = document.getElementById('resTravelTips');
    const copyPlanBtn = document.getElementById('copyPlanBtn');
    const printPlanBtn = document.getElementById('printPlanBtn');
    const newPlanBtn = document.getElementById('newPlanBtn');

    let currentPlanData = null;
    let loadingInterval = null;

    // 1. 인기 추천 여행지 칩 클릭 이벤트
    chipBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            destinationInput.value = btn.dataset.dest;
            destinationInput.focus();
        });
    });

    // 2. 여행 스타일 카드 선택 상태 토글
    styleCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
            card.classList.add('active');
        }

        card.addEventListener('click', (e) => {
            // 레이블 클릭 기본 동작과 중복 방지
            if (e.target.tagName !== 'INPUT') {
                checkbox.checked = !checkbox.checked;
            }
            if (checkbox.checked) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
    });

    // 3. 로딩 상태 메시지 순환
    const loadingMessages = [
        "선택하신 여행지의 최신 핫플레이스를 분석하고 있습니다...",
        "동선이 꼬이지 않도록 최적의 시간표를 계산하고 있습니다...",
        "현지 로컬 맛집과 뷰 맛집 카페를 선별하고 있습니다...",
        "여행에 꼭 필요한 맞춤 준비물과 유용한 꿀팁을 정리하고 있습니다...",
        "거의 다 되었습니다! 멋진 일정을 완성하는 중입니다..."
    ];

    function startLoadingAnimation() {
        let msgIndex = 0;
        loadingStatusText.textContent = loadingMessages[0];
        loadingInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % loadingMessages.length;
            loadingStatusText.textContent = loadingMessages[msgIndex];
        }, 2200);
    }

    function stopLoadingAnimation() {
        if (loadingInterval) {
            clearInterval(loadingInterval);
            loadingInterval = null;
        }
    }

    // 4. 폼 제출 및 일정 생성 API 호출
    planForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const destination = destinationInput.value.trim();
        if (!destination) {
            alert('여행지를 입력해주세요!');
            destinationInput.focus();
            return;
        }

        const duration = document.getElementById('duration').value;
        const companion = document.getElementById('companion').value;
        const budget = document.getElementById('budget').value;
        const notes = document.getElementById('notes').value.trim();

        // 선택된 스타일 목록 추출
        const checkedStyles = Array.from(document.querySelectorAll('input[name="styles"]:checked'))
            .map(cb => cb.value);

        // UI 상태 전환: 로딩 표시
        formCard.classList.add('d-none');
        resultContainer.classList.add('d-none');
        loadingCard.classList.remove('d-none');
        startLoadingAnimation();

        try {
            const response = await fetch('/api/generate-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    destination,
                    duration,
                    companion,
                    budget,
                    notes,
                    styles: checkedStyles
                })
            });

            if (!response.ok) {
                throw new Error(`서버 오류 발생 (${response.status})`);
            }

            const data = await response.json();
            currentPlanData = data;
            renderPlanResult(data);

        } catch (error) {
            console.error('일정 생성 실패:', error);
            alert('일정을 생성하는 도중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
            // 폼 복귀
            formCard.classList.remove('d-none');
        } finally {
            stopLoadingAnimation();
            loadingCard.classList.add('d-none');
        }
    });

    // 5. 생성된 일정 데이터 화면 렌더링
    function renderPlanResult(data) {
        // 기본 정보 렌더링
        resTitle.textContent = data.title || `${data.destination} 여행 일정`;
        resSummary.textContent = data.summary || '';
        resDestination.textContent = `📍 ${data.destination}`;
        resDuration.textContent = `⏱️ ${data.duration}`;
        resBudget.textContent = `💰 ${data.estimated_budget || '예산 맞춤'}`;

        // 탭 및 타임라인 초기화
        dayTabs.innerHTML = '';
        dayTabsContent.innerHTML = '';

        const dailyPlans = data.daily_plans || [];

        dailyPlans.forEach((dayPlan, index) => {
            const dayNum = dayPlan.day || (index + 1);
            const tabId = `day-${dayNum}-tab`;
            const contentId = `day-${dayNum}-content`;
            const isActive = index === 0;

            // 탭 버튼 생성
            const tabItem = document.createElement('li');
            tabItem.className = 'nav-item';
            tabItem.innerHTML = `
                <button class="nav-link ${isActive ? 'active' : ''}" id="${tabId}" data-bs-toggle="pill" data-bs-target="#${contentId}" type="button" role="tab">
                    Day ${dayNum}
                </button>
            `;
            dayTabs.appendChild(tabItem);

            // 타임라인 일정 항목들 생성
            const schedules = dayPlan.schedule || [];
            let scheduleItemsHtml = '';

            schedules.forEach(item => {
                const category = item.category || '명소';
                const catClass = `badge-cat-${category}`;

                scheduleItemsHtml += `
                    <div class="timeline-item">
                        <div class="timeline-marker"></div>
                        <div class="timeline-content">
                            <div class="d-flex justify-content-between align-items-center mb-1 flex-wrap gap-1">
                                <span class="timeline-time">${item.time || ''}</span>
                                <span class="badge rounded-pill ${catClass} px-2 py-1 small">${category}</span>
                            </div>
                            <h5 class="fw-bold mb-2 text-dark">${item.place || ''}</h5>
                            <p class="text-secondary mb-2 small">${item.description || ''}</p>
                            ${item.tip ? `
                                <div class="timeline-tip">
                                    <i class="fa-solid fa-lightbulb me-1"></i><strong>Tip:</strong> ${item.tip}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });

            // 탭 콘텐츠 영역 생성
            const contentPane = document.createElement('div');
            contentPane.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
            contentPane.id = contentId;
            contentPane.role = 'tabpanel';
            contentPane.innerHTML = `
                <div class="mb-4 p-3 bg-light rounded-3 d-flex align-items-center justify-content-between flex-wrap gap-2">
                    <div>
                        <span class="badge bg-primary me-2">Day ${dayNum}</span>
                        <strong class="text-dark fs-6">${dayPlan.theme || '즐거운 여행 일정'}</strong>
                    </div>
                    <span class="small text-muted">총 ${schedules.length}개 코스</span>
                </div>
                <div class="timeline">
                    ${scheduleItemsHtml}
                </div>
            `;
            dayTabsContent.appendChild(contentPane);
        });

        // 준비물 체크리스트 렌더링
        resPackingList.innerHTML = '';
        const packingList = data.packing_list || [];
        packingList.forEach((itemObj, idx) => {
            const itemText = typeof itemObj === 'string' ? itemObj : itemObj.item;
            const isEssential = itemObj.essential;

            const checkDiv = document.createElement('div');
            checkDiv.className = 'checklist-item';
            checkDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" id="pack-${idx}">
                <label class="form-check-label flex-grow-1 cursor-pointer" for="pack-${idx}">
                    <span>${itemText}</span>
                    ${isEssential ? '<span class="badge bg-danger-subtle text-danger ms-2 small">필수</span>' : ''}
                </label>
            `;
            const chk = checkDiv.querySelector('input');
            chk.addEventListener('change', () => {
                checkDiv.classList.toggle('checked', chk.checked);
            });
            resPackingList.appendChild(checkDiv);
        });

        // 여행 꿀팁 렌더링
        resTravelTips.innerHTML = '';
        const tips = data.travel_tips || [];
        tips.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            resTravelTips.appendChild(li);
        });

        // 결과 화면 표시 및 스크롤
        resultContainer.classList.remove('d-none');
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // 6. 전체 일정 클립보드 복사
    copyPlanBtn.addEventListener('click', () => {
        if (!currentPlanData) return;

        let copyText = `✈️ [${currentPlanData.title}]\n`;
        copyText += `📍 여행지: ${currentPlanData.destination} | 기간: ${currentPlanData.duration}\n`;
        copyText += `💬 요약: ${currentPlanData.summary}\n\n`;

        (currentPlanData.daily_plans || []).forEach(dp => {
            copyText += `━━━━━━━━━━━━━━━━━━━━\n`;
            copyText += `📅 Day ${dp.day}: ${dp.theme}\n`;
            (dp.schedule || []).forEach(sc => {
                copyText += `• [${sc.time}] ${sc.place} (${sc.category})\n  - ${sc.description}\n`;
                if (sc.tip) copyText += `  💡 Tip: ${sc.tip}\n`;
            });
            copyText += `\n`;
        });

        if (currentPlanData.travel_tips && currentPlanData.travel_tips.length > 0) {
            copyText += `💡 [현지 여행 꿀팁]\n`;
            currentPlanData.travel_tips.forEach(t => copyText += `- ${t}\n`);
        }

        navigator.clipboard.writeText(copyText)
            .then(() => alert('일정 요약이 클립보드에 복사되었습니다! 친구나 단톡방에 공유해보세요.'))
            .catch(() => alert('복사에 실패했습니다. 권한을 확인해주세요.'));
    });

    // 7. 인쇄 / PDF 저장
    printPlanBtn.addEventListener('click', () => {
        window.print();
    });

    // 8. 새 일정 계획하기 (리셋)
    newPlanBtn.addEventListener('click', () => {
        resultContainer.classList.add('d-none');
        formCard.classList.remove('d-none');
        formCard.scrollIntoView({ behavior: 'smooth' });
    });
});
