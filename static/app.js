const sourceText = document.getElementById("source-text")
const userNote = document.getElementById("user-note")
const sourceFile = document.getElementById("source-file")
const fileName = document.getElementById("file-name")
const wordCount = document.getElementById("word-count")
const charCount = document.getElementById("char-count")
const refineForm = document.getElementById("refine-form")
const includeAnalysis = document.getElementById("include-analysis")
const submitButton = document.getElementById("submit-button")
const analyzeButton = document.getElementById("analyze-button")
const resourcesForm = document.getElementById("resources-form")
const resourceQuery = document.getElementById("resource-query")
const flash = document.getElementById("flash")
const resultMeta = document.getElementById("result-meta")
const variantsGrid = document.getElementById("variants-grid")
const questionsList = document.getElementById("questions-list")
const structuredOutput = document.getElementById("structured-output")
const validationList = document.getElementById("validation-list")
const analysisResult = document.getElementById("analysis-result")
const resourcesResult = document.getElementById("resources-result")
const copyStructured = document.getElementById("copy-structured")
const importFileButton = document.getElementById("import-file")
const paraphraseForm = document.getElementById("paraphrase-form")
const paraphraseTone = document.getElementById("paraphrase-tone")
const paraphraseIntensity = document.getElementById("paraphrase-intensity")
const paraphraseIntensityValue = document.getElementById("paraphrase-intensity-value")
const paraphraseButton = document.getElementById("paraphrase-button")
const paraphraseResult = document.getElementById("paraphrase-result")

function updateCounts() {
  const text = sourceText.value.trim()
  const words = text ? text.split(/\s+/).length : 0
  wordCount.textContent = `${words} parole`
  charCount.textContent = `${sourceText.value.length} caratteri`
}

function setFlash(message, tone = "neutral") {
  flash.textContent = message
  flash.className = `flash flash-${tone}`
}

function setLoading(button, loading, label) {
  if (!button) return
  if (loading) {
    button.dataset.originalLabel = button.textContent
    button.textContent = label
    button.disabled = true
    return
  }
  button.textContent = button.dataset.originalLabel || button.textContent
  button.disabled = false
}

async function fetchJson(url, options) {
  const response = await fetch(url, options)
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.error || "Richiesta non riuscita.")
  }
  return payload
}

function renderValidation(errors) {
  if (!errors || errors.length === 0) {
    validationList.textContent = "Controllo strutturale superato."
    return
  }

  validationList.innerHTML = errors
    .map((error) => `<div>• ${escapeHtml(error)}</div>`)
    .join("")
}

function renderQuestions(questions) {
  if (!questions || questions.length === 0) {
    questionsList.innerHTML = "<li>Nessuna domanda aggiuntiva.</li>"
    return
  }

  questionsList.innerHTML = questions.map((question) => `<li>${question}</li>`).join("")
}

function renderVariants(variants) {
  if (!variants || variants.length === 0) {
    variantsGrid.innerHTML = ""
    return
  }

  variantsGrid.innerHTML = variants
    .map(
      (variant) => `
        <article class="variant-card">
          <div>
            <h3>${variant.label}</h3>
            <p class="variant-note">${escapeHtml(variant.note || "Nessuna nota aggiuntiva.")}</p>
          </div>
          <div class="variant-output">${escapeHtml(variant.text)}</div>
          <div class="variant-actions">
            <button class="variant-button" type="button" data-use-variant="${variant.id}">Usa come nuova base</button>
            <button class="variant-button" type="button" data-copy-variant="${variant.id}">Copia testo</button>
          </div>
        </article>
      `
    )
    .join("")

  for (const button of variantsGrid.querySelectorAll("[data-use-variant]")) {
    button.addEventListener("click", () => {
      const selected = variants.find((item) => item.id === button.dataset.useVariant)
      if (!selected) return
      sourceText.value = selected.text
      sourceFile.value = ""
      fileName.textContent = "Nessun file selezionato."
      updateCounts()
      sourceText.focus()
      sourceText.scrollIntoView({ behavior: "smooth", block: "start" })
      setFlash(`La variante ${selected.label.toLowerCase()} è diventata il nuovo testo di lavoro.`, "success")
    })
  }

  for (const button of variantsGrid.querySelectorAll("[data-copy-variant]")) {
    button.addEventListener("click", async () => {
      const selected = variants.find((item) => item.id === button.dataset.copyVariant)
      if (!selected) return
      await navigator.clipboard.writeText(selected.text)
      setFlash(`Variante ${selected.label.toLowerCase()} copiata negli appunti.`, "success")
    })
  }
}

function renderAnalysis(payload) {
  if (!payload) return

  if (!payload.available) {
    analysisResult.className = "utility-result"
    analysisResult.innerHTML = `<p class="muted-copy">${escapeHtml(payload.message || "Analisi non disponibile.")}</p>`
    return
  }

  const lemmaTags = (payload.key_lemmas || [])
    .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
    .join("")

  const repeatedTags = (payload.repeated_lemmas || [])
    .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
    .join("")

  analysisResult.className = "utility-result"
  analysisResult.innerHTML = `
    <p class="muted-copy">${escapeHtml(payload.message || "")}</p>
    <div class="stats-grid">
      <div class="stat-card"><strong>${payload.sentence_count || 0}</strong> frasi</div>
      <div class="stat-card"><strong>${payload.average_sentence_length || 0}</strong> parole medie</div>
      <div class="stat-card"><strong>${payload.token_count || 0}</strong> token</div>
      <div class="stat-card"><strong>${escapeHtml(payload.model || "n/d")}</strong> modello</div>
    </div>
    <div class="tag-list">${lemmaTags || '<span class="muted-copy">Nessun lemma chiave.</span>'}</div>
    <div class="tag-list">${repeatedTags || '<span class="muted-copy">Nessuna ripetizione rilevante.</span>'}</div>
  `
}

function renderResources(payload) {
  const lexical = payload.lexical
  const texts = payload.texts || []

  let html = `<p class="muted-copy">${escapeHtml(payload.message || "")}</p>`

  if (lexical) {
    const definitions = (lexical.definitions || [])
      .map((item) => `<li>${escapeHtml(item)}</li>`)
      .join("")

    const synonyms = (lexical.synonyms || [])
      .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
      .join("")

    const antonyms = (lexical.antonyms || [])
      .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
      .join("")

    html += `
      <div class="resource-block">
        <a class="link-pill" href="${lexical.page_url}" target="_blank" rel="noreferrer">${escapeHtml(lexical.title)}</a>
        ${definitions ? `<ol class="definition-list">${definitions}</ol>` : ""}
        ${synonyms ? `<div class="tag-list">${synonyms}</div>` : ""}
        ${antonyms ? `<div class="tag-list">${antonyms}</div>` : ""}
      </div>
    `
  }

  if (texts.length > 0) {
    html += `
      <div class="link-list">
        ${texts
          .map(
            (item) =>
              `<a class="link-pill" href="${item.url}" target="_blank" rel="noreferrer">${escapeHtml(item.title)}</a>`
          )
          .join("")}
      </div>
    `
  }

  if (!lexical && texts.length === 0) {
    html += '<p class="muted-copy">Nessun risultato disponibile per questa ricerca.</p>'
  }

  resourcesResult.className = "utility-result"
  resourcesResult.innerHTML = html
}

function renderParaphrase(payload) {
  if (!payload || !payload.text) {
    paraphraseResult.className = "utility-result empty-state"
    paraphraseResult.textContent = "Nessuna parafrasi generata."
    return
  }

  paraphraseResult.className = "utility-result"
  paraphraseResult.innerHTML = `
    <div class="paraphrase-actions">
      <button class="variant-button" type="button" data-paraphrase-use>Usa come testo</button>
      <button class="variant-button" type="button" data-paraphrase-copy>Copia testo</button>
    </div>
    <div class="variant-output">${escapeHtml(payload.text)}</div>
  `

  const useButton = paraphraseResult.querySelector("[data-paraphrase-use]")
  const copyButton = paraphraseResult.querySelector("[data-paraphrase-copy]")

  if (useButton) {
    useButton.addEventListener("click", () => {
      sourceText.value = payload.text
      sourceFile.value = ""
      fileName.textContent = "Nessun file selezionato."
      updateCounts()
      sourceText.focus()
      setFlash("Parafrasi applicata come nuovo testo di lavoro.", "success")
    })
  }

  if (copyButton) {
    copyButton.addEventListener("click", async () => {
      await navigator.clipboard.writeText(payload.text)
      setFlash("Parafrasi copiata negli appunti.", "success")
    })
  }
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
}

for (const chip of document.querySelectorAll("[data-fill-note]")) {
  chip.addEventListener("click", () => {
    userNote.value = chip.dataset.fillNote || ""
    userNote.focus()
  })
}

refineForm.addEventListener("submit", async (event) => {
  event.preventDefault()
  setLoading(submitButton, true, "Sto generando...")
  setFlash("Sto costruendo le sei varianti.", "neutral")

  try {
    const payload = await fetchJson("/api/refine", {
      method: "POST",
      body: new FormData(refineForm),
    })

    const source = payload.meta?.source || "editor"
    const words = payload.meta?.words || 0
    const chars = payload.meta?.characters || 0
    const noteText = payload.meta?.note_used ? "Nota di regia applicata." : "Nessuna nota aggiuntiva."

    resultMeta.textContent = `${words} parole, ${chars} caratteri. Sorgente: ${source}. ${noteText}`
    structuredOutput.value = payload.structured_output || ""
    renderValidation(payload.errors)
    renderQuestions(payload.questions)
    renderVariants(payload.variants)

    if (includeAnalysis.checked && payload.analysis) {
      renderAnalysis(payload.analysis)
    }

    setFlash("Varianti generate correttamente.", "success")
  } catch (error) {
    setFlash(error.message || "Errore durante la generazione.", "error")
  } finally {
    setLoading(submitButton, false, "Sto generando...")
  }
})

if (importFileButton) {
  importFileButton.addEventListener("click", async () => {
    const file = sourceFile.files?.[0]
    if (!file) {
      setFlash("Seleziona un file da importare.", "error")
      return
    }

    setLoading(importFileButton, true, "Importo...")
    const extension = file.name.split(".").pop()?.toLowerCase()
    const isPlainText = extension === "txt" || extension === "md"

    try {
      if (isPlainText) {
        const content = await file.text()
        sourceText.value = content.trim()
        updateCounts()
        setFlash("Testo importato dal file selezionato.", "success")
        return
      }

      const formData = new FormData()
      formData.append("file", file)
      const payload = await fetchJson("/api/extract", {
        method: "POST",
        body: formData,
      })
      sourceText.value = payload.text || ""
      updateCounts()
      setFlash(`Testo importato da ${payload.source || "file"}.`, "success")
    } catch (error) {
      setFlash(error.message || "Errore durante l'importazione.", "error")
    } finally {
      setLoading(importFileButton, false, "Importo...")
    }
  })
}

analyzeButton.addEventListener("click", async () => {
  const text = sourceText.value.trim()
  if (!text) {
    setFlash("Inserisci prima un testo da analizzare.", "error")
    return
  }

  setLoading(analyzeButton, true, "Analizzo...")
  try {
    const payload = await fetchJson("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    })
    renderAnalysis(payload)
    setFlash("Analisi completata.", "success")
  } catch (error) {
    setFlash(error.message || "Errore durante l'analisi.", "error")
  } finally {
    setLoading(analyzeButton, false, "Analizzo...")
  }
})

resourcesForm.addEventListener("submit", async (event) => {
  event.preventDefault()
  const query = resourceQuery.value.trim()
  if (!query) {
    setFlash("Inserisci un termine da cercare.", "error")
    return
  }

  try {
    const payload = await fetchJson(`/api/resources?q=${encodeURIComponent(query)}`, {
      method: "GET",
    })
    renderResources(payload)
    setFlash("Risorse recuperate.", "success")
  } catch (error) {
    setFlash(error.message || "Errore durante la ricerca.", "error")
  }
})

if (paraphraseForm) {
  paraphraseForm.addEventListener("submit", async (event) => {
    event.preventDefault()
    const text = sourceText.value.trim()
    if (!text) {
      setFlash("Inserisci prima un testo da parafrasare.", "error")
      return
    }

    const intensityValue = Number(paraphraseIntensity?.value || "35") / 100
    setLoading(paraphraseButton, true, "Genero...")

    try {
      const payload = await fetchJson("/api/paraphrase", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          tone: paraphraseTone?.value || "neutral",
          intensity: intensityValue,
        }),
      })
      renderParaphrase(payload)
      setFlash("Parafrasi generata.", "success")
    } catch (error) {
      setFlash(error.message || "Errore durante la parafrasi.", "error")
    } finally {
      setLoading(paraphraseButton, false, "Genero...")
    }
  })
}

copyStructured.addEventListener("click", async () => {
  if (!structuredOutput.value.trim()) {
    setFlash("Non c'è ancora un output completo da copiare.", "error")
    return
  }
  await navigator.clipboard.writeText(structuredOutput.value)
  setFlash("Output completo copiato negli appunti.", "success")
})

sourceText.addEventListener("input", updateCounts)
sourceFile.addEventListener("change", () => {
  const file = sourceFile.files?.[0]
  fileName.textContent = file ? `File selezionato: ${file.name}` : "Nessun file selezionato."
})

if (paraphraseIntensity && paraphraseIntensityValue) {
  paraphraseIntensity.addEventListener("input", () => {
    paraphraseIntensityValue.textContent = `${paraphraseIntensity.value}%`
  })
}

updateCounts()
