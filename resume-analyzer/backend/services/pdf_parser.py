import fitz


def extract_text_from_pdf(file):

    if file is None:
        raise ValueError(
            "No PDF file was provided."
        )

    try:

        pdf_bytes = file.read()

        if not pdf_bytes:
            raise ValueError(
                "The uploaded PDF is empty."
            )

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if document.page_count == 0:

            document.close()

            raise ValueError(
                "The PDF does not contain any pages."
            )

        pages = []

        for page in document:

            text = page.get_text()

            if text:
                pages.append(text)

        document.close()

        extracted_text = "\n".join(
            pages
        ).strip()

        if not extracted_text:

            raise ValueError(
                "No readable text was found in the PDF."
            )

        return extracted_text

    except ValueError:

        raise

    except Exception as error:

        raise ValueError(
            f"Unable to read the PDF: {error}"
        )


if __name__ == "__main__":

    print(
        "PDF parser loaded successfully."
    )