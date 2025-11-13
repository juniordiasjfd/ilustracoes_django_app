function exportTableToCSV(tableId, filename) {
    // 1. Usa o tableId passado como parâmetro para encontrar o elemento
    const table = document.getElementById(tableId);
    
    // Verifica se a tabela foi encontrada
    if (!table) {
      console.error(`Tabela com ID "${tableId}" não encontrada.`);
      return;
    }
    
    let rows = table.querySelectorAll('tr');
    let csvContent = '';
  
    rows.forEach(row => {
      // Note: Usar 'td, th' garante que tanto o cabeçalho quanto o corpo sejam incluídos
      let cols = row.querySelectorAll('td, th'); 
      let rowData = [];
      
      // Adicione aspas duplas e escape de aspas para lidar com dados que contenham vírgulas ou quebras de linha
      cols.forEach(col => {
        let text = col.innerText.replace(/"/g, '""'); // Escapa aspas
        rowData.push(`"${text}"`);
      });
      
      csvContent += rowData.join(',') + '\n';
    });
  
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); // Adiciona charset para UTF-8
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    
    // Anexa e clica para iniciar o download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }



function exportTable(tableId, format = 'xlsx', filename = 'table-data') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error(`Tabela com ID "${tableId}" não encontrada.`);
        return;
    }

    const instance = new TableExport(table, {
        formats: [format],
        exportButtons: false,
        filename: filename,
    });

    const exportData = instance.getExportData()[tableId][format];
    instance.export2file(
        exportData.data,
        exportData.mimeType,
        exportData.filename,
        exportData.fileExtension
    );
}