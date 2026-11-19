import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gafia_docs


class IndexTest(unittest.TestCase):
    def test_document_is_indexed_retrieved_and_detects_changes(self):
        from llama_index.core import Settings
        from llama_index.core.embeddings import MockEmbedding
        from llama_index.core.llms import MockLLM

        def configure_mock():
            Settings.llm = MockLLM(max_tokens=64)
            Settings.embed_model = MockEmbedding(embed_dim=8)
            Settings.chunk_size = 512
            Settings.chunk_overlap = 64

        with tempfile.TemporaryDirectory(dir=gafia_docs.ROOT) as location:
            root = Path(location)
            documents = root / "documentos"
            documents.mkdir()
            source = documents / "manual.txt"
            source.write_text("O GAFIA mantém indicadores do projeto de Iracemápolis.", encoding="utf-8")
            with (
                patch.object(gafia_docs, "ROOT", root),
                patch.object(gafia_docs, "DOCUMENTS", documents),
                patch.object(gafia_docs, "INDEX_DIR", root / ".local_index"),
                patch.object(gafia_docs, "configure_llamaindex", side_effect=configure_mock),
            ):
                self.assertEqual(gafia_docs.build_index(), 1)
                index = gafia_docs.load_index()
                result = gafia_docs.answer(index, "Sobre qual projeto são os indicadores?")
                self.assertTrue(result["resposta"])
                self.assertEqual(result["fontes"][0]["arquivo"], "documentos/manual.txt")
                source.write_text("Conteúdo atualizado.", encoding="utf-8")
                self.assertFalse(gafia_docs.index_status()[0])


if __name__ == "__main__":
    unittest.main()
