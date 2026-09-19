Office.onReady(() => {
    document.getElementById("btnHumanize").onclick = humanizeText;
    document.getElementById("btnInsert").onclick = insertText;
});

async function humanizeText() {
    const statusDiv = document.getElementById("status");
    const resultArea = document.getElementById("resultArea");
    const btnHumanize = document.getElementById("btnHumanize");
    
    try {
        statusDiv.className = "status loading";
        statusDiv.textContent = "⏳ Analyse du texte en cours...";
        btnHumanize.disabled = true;
        
        await Word.run(async (context) => {
            const selection = context.document.getSelection();
            selection.load("text");
            await context.sync();
            
            const originalText = selection.text;
            
            if (!originalText.trim()) {
                throw new Error("Veuillez sélectionner du texte dans Word");
            }
            
            statusDiv.textContent = " Envoi à l'IA locale (Mistral 7B)...";
            
            const response = await fetch("http://localhost:5001/humanize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: originalText })
            });
            
            if (!response.ok) {
                throw new Error(`Erreur serveur: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            resultArea.value = data.humanized_text;
            
            statusDiv.className = "status success";
            statusDiv.textContent = "✅ Texte humanisé avec succès !";
        });
        
    } catch (error) {
        console.error(error);
        statusDiv.className = "status error";
        statusDiv.textContent = `❌ Erreur: ${error.message}`;
    } finally {
        btnHumanize.disabled = false;
    }
}

async function insertText() {
    const resultArea = document.getElementById("resultArea");
    const textToInsert = resultArea.value;
    
    if (!textToInsert.trim()) {
        alert("Aucun texte à insérer");
        return;
    }
    
    try {
        await Word.run(async (context) => {
            const selection = context.document.getSelection();
            selection.insertText(textToInsert, "Replace");
            await context.sync();
        });
        
        const statusDiv = document.getElementById("status");
        statusDiv.className = "status success";
        statusDiv.textContent = "✅ Texte inséré dans Word !";
        
    } catch (error) {
        console.error(error);
        alert("Erreur lors de l'insertion: " + error.message);
    }
}
