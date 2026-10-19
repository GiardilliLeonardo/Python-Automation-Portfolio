# Task: Simple Python Script Needed – Small Project ($10 Fixed Budget)

import csv
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurazione del logging per un output professionale
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def process_csv(input_path: Path, output_path: Path) -> None:
    """
    Legge un file CSV, pulisce i dati (rimuove righe vuote e spazi bianchi),
    e salva il risultato in un nuovo file CSV.
    """
    if not input_path.exists():
        logging.error(f"Il file di input non esiste: {input_path}")
        return

    try:
        logging.info(f"Inizio lettura del file: {input_path}")
        
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames:
                logging.error("Il file CSV è vuoto o manca l'intestazione.")
                return
            
            # Pulizia delle intestazioni
            headers: List[str] = [str(header).strip() for header in reader.fieldnames if header]
            
            processed_data: List[Dict[str, Any]] = []
            
            for row_num, row in enumerate(reader, start=2):
                # Salta le righe completamente vuote
                if not any(value.strip() for value in row.values() if value):
                    continue
                
                # Pulizia dei dati: rimozione spazi bianchi iniziali e finali
                cleaned_row: Dict[str, str] = {}
                for key, value in row.items():
                    if key:
                        clean_key = str(key).strip()
                        clean_value = str(value).strip() if value else ""
                        cleaned_row[clean_key] = clean_value
                
                processed_data.append(cleaned_row)

        logging.info(f"Letti e puliti {len(processed_data)} record. Scrittura in corso...")

        # Creazione della directory di output se non esiste
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(processed_data)
            
        logging.info(f"Automazione completata con successo. File salvato in: {output_path}")

    except PermissionError:
        logging.error("Errore di permessi: assicurati che il file non sia aperto in un altro programma.")
    except Exception as e:
        logging.error(f"Si è verificato un errore imprevisto: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Script di automazione CSV: pulizia e formattazione dei dati."
    )
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        required=True, 
        help="Percorso del file CSV di input"
    )
    parser.add_argument(
        "-o", "--output",
