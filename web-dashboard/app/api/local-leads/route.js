import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), '../data/raw');
    
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json({ error: 'data/raw directory not found', leads: [] });
    }

    const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.csv'));
    let allLeads = [];

    // Basic CSV parser for this specific use case
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

    for (const file of files) {
      const content = fs.readFileSync(path.join(dataDir, file), 'utf-8');
      const lines = content.split('\n').filter(l => l.trim() !== '');
      if (lines.length <= 1) continue;
      
      const headers = parseCSVLine(lines[0]).map(h => h.trim());
      
      for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length !== headers.length) continue;
        
        let lead = { sourceFile: file };
        headers.forEach((header, index) => {
          lead[header] = values[index] ? values[index].trim() : '';
        });
        allLeads.push(lead);
      }
    }

    return NextResponse.json({ leads: allLeads });
  } catch (error) {
    console.error('Error reading local leads:', error);
    return NextResponse.json({ error: error.message, leads: [] }, { status: 500 });
  }
}
