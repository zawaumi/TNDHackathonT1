let plans = [];
let selectedPlanId = null;

const planForm = document.getElementById('plan-form');
const adjustForm = document.getElementById('adjust-form');
const planList = document.getElementById('plan-list');
const statusText = document.getElementById('plan-status');
const generateBtn = document.getElementById('generate-btn');
const adjustBtn = document.getElementById('adjust-btn');
const deleteBtn = document.getElementById('delete-btn');
const detailTitle = document.getElementById('detail-title');
const detailSummary = document.getElementById('detail-summary');
const detailMetrics = document.getElementById('detail-metrics');
const weeklyFocus = document.getElementById('weekly-focus');
const dayGrid = document.getElementById('day-grid');
const startDateInput = document.getElementById('start_date');

function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    const value = `; ${document.cookie}`;
    const parts = value.split('; csrftoken=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function numberValue(formData, key) {
    const value = formData.get(key);
    if (value === null || value === '') return undefined;
    return Number(value);
}

function textValue(formData, key) {
    const value = formData.get(key);
    return value === null ? '' : String(value);
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            ...(options.headers || {}),
        },
    });
    const data = response.status === 204 ? null : await response.json();
    if (!response.ok) {
        const message = data?.detail || JSON.stringify(data);
        throw new Error(message);
    }
    return data;
}

function setStatus(message) {
    statusText.textContent = message;
}

function selectedPlan() {
    return plans.find((plan) => plan.id === selectedPlanId) || null;
}

function buildGeneratePayload() {
    const formData = new FormData(planForm);
    const payload = {
        goal: textValue(formData, 'goal'),
        goal_detail: textValue(formData, 'goal_detail'),
        height_cm: numberValue(formData, 'height_cm'),
        weight_kg: numberValue(formData, 'weight_kg'),
        age: numberValue(formData, 'age'),
        gender: textValue(formData, 'gender'),
        experience_level: textValue(formData, 'experience_level'),
        training_days_per_week: numberValue(formData, 'training_days_per_week'),
        food_preferences: textValue(formData, 'food_preferences'),
        allergies: textValue(formData, 'allergies'),
        request_text: textValue(formData, 'request_text'),
        generate_images: formData.get('generate_images') === 'on',
    };
    const startDate = textValue(formData, 'start_date');
    if (startDate) payload.start_date = startDate;
    Object.keys(payload).forEach((key) => payload[key] === undefined && delete payload[key]);
    return payload;
}

async function loadPlans() {
    setStatus('読み込み中');
    plans = await requestJson('/api/ai/plans/');
    renderList();
    if (plans.length > 0) {
        selectedPlanId = plans[0].id;
        renderDetail();
    }
    setStatus('');
}

function renderList() {
    if (plans.length === 0) {
        planList.innerHTML = '<div class="empty-state">保存済みプランはまだありません。</div>';
        return;
    }
    planList.innerHTML = plans.map((plan) => `
        <button class="plan-card ${plan.id === selectedPlanId ? 'is-active' : ''}" type="button" data-plan-id="${plan.id}">
            <strong>${escapeHtml(plan.title)}</strong>
            <span>${escapeHtml(plan.plan?.summary || '')}</span>
            <span class="meta-row">
                <span class="pill">${escapeHtml(plan.provider)}</span>
                <span>${escapeHtml(plan.start_date)}</span>
                <span>${escapeHtml(plan.status)}</span>
            </span>
        </button>
    `).join('');
    document.querySelectorAll('[data-plan-id]').forEach((button) => {
        button.addEventListener('click', () => {
            selectedPlanId = Number(button.dataset.planId);
            renderList();
            renderDetail();
        });
    });
}

function renderDetail() {
    const planRecord = selectedPlan();
    if (!planRecord) {
        detailTitle.textContent = 'プラン未選択';
        detailSummary.textContent = '生成するとここに内容が表示されます。';
        detailMetrics.innerHTML = '';
        weeklyFocus.innerHTML = '';
        dayGrid.innerHTML = '';
        adjustBtn.disabled = true;
        deleteBtn.disabled = true;
        return;
    }
    const plan = planRecord.plan || {};
    detailTitle.textContent = plan.plan_title || planRecord.title;
    detailSummary.textContent = plan.summary || '';
    detailMetrics.innerHTML = `
        ${metricHtml('目標カロリー', `${plan.daily_calorie_target || 0} kcal`)}
        ${metricHtml('たんぱく質', `${plan.macro_targets?.protein_g || 0} g`)}
        ${metricHtml('炭水化物', `${plan.macro_targets?.carbs_g || 0} g`)}
        ${metricHtml('脂質', `${plan.macro_targets?.fat_g || 0} g`)}
    `;
    weeklyFocus.innerHTML = (plan.weekly_training_focus || []).map((item) => `
        <div class="metric">
            <span>Week ${escapeHtml(item.week)}</span>
            <strong>${escapeHtml(item.focus)}</strong>
        </div>
    `).join('');
    dayGrid.innerHTML = (plan.days || []).map(dayHtml).join('');
    adjustBtn.disabled = false;
    deleteBtn.disabled = false;
}

function metricHtml(label, value) {
    return `
        <div class="metric">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
        </div>
    `;
}

function dayHtml(day) {
    const training = day.training || {};
    const exercises = (training.exercises || []).slice(0, 4).map((exercise) => (
        `<li>${escapeHtml(exercise.name)} ${escapeHtml(exercise.sets)}set ${escapeHtml(exercise.reps)}</li>`
    )).join('');
    const firstMeal = (day.meals || [])[0] || {};
    const imageUrl = firstMeal.recipe?.image_url || '';
    const mealPreview = imageUrl ? `
        <div class="meal-preview">
            <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(firstMeal.title || 'recipe')}">
            <div>
                <strong>${escapeHtml(firstMeal.title || '')}</strong>
                <div class="meta-row">
                    <span>${escapeHtml(firstMeal.calories || 0)} kcal</span>
                    <span>P ${escapeHtml(firstMeal.protein_g || 0)}g</span>
                </div>
            </div>
        </div>
    ` : '';
    return `
        <article class="day-card">
            <div>
                <h3>Day ${escapeHtml(day.day_number)} ${escapeHtml(day.date)}</h3>
                <div class="meta-row">
                    <span class="pill">${escapeHtml(training.type || '')}</span>
                    <span>${escapeHtml(training.duration_minutes || 0)}分</span>
                </div>
            </div>
            <strong>${escapeHtml(training.title || '')}</strong>
            <ul class="compact-list">${exercises}</ul>
            ${mealPreview}
        </article>
    `;
}

if (startDateInput) {
    startDateInput.value = new Date().toISOString().slice(0, 10);
}

if (planForm) {
    planForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        generateBtn.disabled = true;
        setStatus('生成中');
        try {
            const created = await requestJson('/api/ai/plans/generate/', {
                method: 'POST',
                body: JSON.stringify(buildGeneratePayload()),
            });
            plans = [created, ...plans.filter((plan) => plan.id !== created.id)];
            selectedPlanId = created.id;
            renderList();
            renderDetail();
            setStatus('生成しました');
        } catch (error) {
            setStatus(error.message);
        } finally {
            generateBtn.disabled = false;
        }
    });
}

if (adjustForm) {
    adjustForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const planRecord = selectedPlan();
        if (!planRecord) return;
        const formData = new FormData(adjustForm);
        const payload = {
            request_text: textValue(formData, 'request_text'),
            generate_images: formData.get('generate_images') === 'on',
        };
        adjustBtn.disabled = true;
        setStatus('調整中');
        try {
            const updated = await requestJson(`/api/ai/plans/${planRecord.id}/adjust/`, {
                method: 'POST',
                body: JSON.stringify(payload),
            });
            plans = [updated, ...plans.filter((plan) => plan.id !== updated.id)];
            selectedPlanId = updated.id;
            adjustForm.reset();
            renderList();
            renderDetail();
            setStatus('調整しました');
        } catch (error) {
            setStatus(error.message);
        } finally {
            adjustBtn.disabled = false;
        }
    });
}

if (deleteBtn) {
    deleteBtn.addEventListener('click', async () => {
        const planRecord = selectedPlan();
        if (!planRecord) return;
        deleteBtn.disabled = true;
        setStatus('削除中');
        try {
            await requestJson(`/api/ai/plans/${planRecord.id}/`, { method: 'DELETE' });
            plans = plans.filter((plan) => plan.id !== planRecord.id);
            selectedPlanId = plans[0]?.id || null;
            renderList();
            renderDetail();
            setStatus('削除しました');
        } catch (error) {
            setStatus(error.message);
        } finally {
            deleteBtn.disabled = false;
        }
    });
}

loadPlans().catch((error) => setStatus(error.message));
