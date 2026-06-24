import { google } from "googleapis";

function buildSheetsError(detail, status = 500, originalError) {
  const error = new Error(`Error: Failed Google Sheets API call - ${detail}`);
  error.status = status;
  if (originalError) {
    error.cause = originalError;
  }
  error.details = detail;
  return error;
}

function extractSheetsErrorDetail(error) {
  if (Array.isArray(error?.errors) && error.errors.length > 0) {
    return error.errors.map(err => err.message).join("; ");
  }
  if (error?.response?.data?.error?.message) {
    return error.response.data.error.message;
  }
  if (typeof error?.message === "string" && error.message.length > 0) {
    return error.message;
  }
  return "Unknown Google Sheets error.";
}

/**
 * Saves a list of leads to a Google Sheet.
 * @param {Array} leads - Array of formatted lead objects.
 * @param {string} category - The search category.
 * @param {string} location - The search location.
 */
export async function saveLeadsToGoogleSheet(leads, category, location) {
  if (!leads || leads.length === 0) {
    console.log("[Sheets] No leads to save to Google Sheets.");
    return;
  }

  const missingEnvVars = [
    !process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL && "GOOGLE_SERVICE_ACCOUNT_EMAIL",
    !process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY && "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY",
    !process.env.GOOGLE_SHEET_ID && "GOOGLE_SHEET_ID"
  ].filter(Boolean);

  if (missingEnvVars.length > 0) {
    const detail = `Missing environment variable(s): ${missingEnvVars.join(", ")}`;
    console.error("[Sheets]", detail);
    throw buildSheetsError(detail);
  }

  console.log(`[Sheets] Attempting to append ${leads.length} leads to Google Sheet.`);

  try {
    const auth = new google.auth.JWT(
      process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      null,
      (process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY || "").replace(/\\n/g, "\n"),
      ["https://www.googleapis.com/auth/spreadsheets"]
    );

    const sheets = google.sheets({ version: "v4", auth });

    // Define headers
    const headers = [
      "Name",
      "Address",
      "Phone",
      "Rating",
      "Website",
      "Category",
      "Location",
      "Date"
    ];

    // Check if sheet is empty (or check first row)
    // For simplicity, we can't easily check without reading.
    // However, the user asked for "Column Naming".
    // A robust way is to read A1:H1, if empty, write headers.

    try {
      const getResponse = await sheets.spreadsheets.values.get({
        spreadsheetId: process.env.GOOGLE_SHEET_ID,
        range: "Sheet1!A1:H1",
      });

      const existingHeaders = getResponse.data.values;
      if (!existingHeaders || existingHeaders.length === 0) {
        console.log("[Sheets] Sheet appears empty or missing headers. Adding headers.");
        await sheets.spreadsheets.values.update({
          spreadsheetId: process.env.GOOGLE_SHEET_ID,
          range: "Sheet1!A1",
          valueInputOption: "USER_ENTERED",
          requestBody: {
            values: [headers],
          },
        });
      }
    } catch (readError) {
      console.warn("[Sheets] Failed to check for existing headers, proceeding to append data:", readError.message);
      // We continue to append data even if header check fails
    }

    // Prepare rows
    const rows = leads.map((lead) => [
      lead.name,
      lead.address,
      lead.phone,
      lead.rating,
      lead.website,
      category,
      location,
      new Date().toISOString()
    ]);

    await sheets.spreadsheets.values.append({
      spreadsheetId: process.env.GOOGLE_SHEET_ID,
      range: "Sheet1!A1", // Append will find the first empty row
      valueInputOption: "USER_ENTERED",
      requestBody: {
        values: rows,
      },
    });

    console.log(`[Sheets] Successfully appended ${rows.length} rows to Google Sheet.`);
  } catch (error) {
    if (error?.message?.startsWith("Error: Failed Google Sheets API call -")) {
      console.error("[Sheets] Google Sheets API call failed:", error.details || error.message);
      throw error;
    }

    const status = typeof error?.code === "number"
      ? error.code
      : error?.response?.status || error?.status || 500;
    const detail = extractSheetsErrorDetail(error);
    console.error("[Sheets] Error saving to Google Sheets:", detail, error?.response?.data || error);
    throw buildSheetsError(detail, status, error);
  }
}
