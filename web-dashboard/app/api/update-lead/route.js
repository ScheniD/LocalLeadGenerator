import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const parseCSVLine = (line) => {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    if (line[i] === '"') {
      inQuotes = !inQuotes;
    } else if (line[i] === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += line[i];
    }
  }
  result.push(current);
  return result;
};

const toCSVLine = (row) => {
  return row.map(cell => {
    // Falls die Variable undefined oder null ist, mach einen leeren String daraus
    const strCell = cell === undefined || cell === null ? '' : String(cell);
    if (strCell.includes(',') || strCell.includes('"') || strCell.includes('\n')) {
      return `"${strCell.replace(/"/g, '""')}"`;
    }
    return strCell;
  }).join(',');
};

export async function POST(request) {
  try {
    const { sourceFile, name, status = 'Yes' } = await request.json();
    
    if (!sourceFile || !name) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    const filePath = path.join(process.cwd(), '../data/raw', sourceFile);
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(l => l.trim() !== '');
    if (lines.length <= 1) return NextResponse.json({ success: true });
    
    let headers = parseCSVLine(lines[0]).map(h => h.trim());
    let contactedIndex = headers.indexOf('Contacted');
    
    // If Contacted column doesn't exist, add it
    if (contactedIndex === -1) {
      headers.push('Contacted');
      contactedIndex = headers.length - 1;
    }
    
    const nameIndex = headers.indexOf('Name');

    const newLines = [toCSVLine(headers)];
    let updated = false;

    for (let i = 1; i < lines.length; i++) {
      let values = parseCSVLine(lines[i]);
      if (values.length < headers.length - 1) continue; // broken row
      
      // Ensure row has same length as headers
      while (values.length < headers.length) {
        values.push('');
      }

      if (values[nameIndex] && values[nameIndex].trim() === name.trim()) {
        values[contactedIndex] = status;
        updated = true;
      }
      newLines.push(toCSVLine(values));
    }

    if (updated) {
      fs.writeFileSync(filePath, newLines.join('\n') + '\n', 'utf-8');
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error updating lead:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
