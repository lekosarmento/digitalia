import uuid
import datetime
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Endereço padrão de homologação do Smart Contract ERC-1155 do DigitalIA na rede Polygon
DEFAULT_CONTRACT_ADDRESS = "0x8Fd9f518d6e32F44208aB59114D32Cd9bC25f7F7"

class BlockchainService:
    """
    Serviço de emissão de certificados Polygon (ERC-1155) com execução simulada rápida.
    Garante conformidade com as assinaturas de API de blockchain reais, eliminando gas fees reais no MVP.
    Retorna UUIDv4 imutável formatado como tx_hash e salva metadados estruturados compatíveis com IPFS.
    """

    @staticmethod
    async def generate_ipfs_metadata(learner_name: str, trail: str, level: int, certificate_id: str) -> Dict[str, Any]:
        """
        Gera a estrutura de metadados padrão ERC-1155 do OpenSea/Polygon no IPFS para o certificado.
        """
        trail_display = trail.replace("_", " ").title()
        return {
            "name": f"Certificado DigitalIA - {trail_display}",
            "description": f"Certificado oficial de capacitação profissional na Trilha {trail_display} emitido pelo programa DigitalIA (ANENO). Nível {level}.",
            "image": f"ipfs://QmDigitalIAPlaceholderHashes/{trail}_level_{level}.png",
            "external_url": f"https://digitalia.aneno.org/certificates/{certificate_id}",
            "attributes": [
                {"trait_type": "Learner Name", "value": learner_name},
                {"trait_type": "Trail", "value": trail},
                {"trait_type": "Level", "value": level},
                {"trait_type": "Issuer", "value": "ANENO - DigitalIA"},
                {"trait_type": "Blockchain Network", "value": "Polygon Mainnet (Mock)"},
                {"trait_type": "Token Standard", "value": "ERC-1155"}
            ]
        }

    @classmethod
    async def issue_certificate(
        cls,
        learner_id: str,
        learner_name: str,
        trail: str,
        level: int
    ) -> Dict[str, Any]:
        """
        Simula a emissão e gravação de um certificado digital (NFT ERC-1155) na Polygon.
        Elimina latência de rede e custos de gas no MVP, retornando dados estruturados
        prontos para persistência na tabela 'certificates'.
        """
        certificate_id = str(uuid.uuid4())
        
        # 1. Gerar os metadados simulados no IPFS
        ipfs_metadata = await cls.generate_ipfs_metadata(learner_name, trail, level, certificate_id)
        
        # 2. Criar hashes simulados de IPFS e de transação Polygon
        ipfs_hash = f"Qm{uuid.uuid4().hex[:44].lower()}"
        tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:32]}"  # 64 caracteres + 0x
        token_id = int(uuid.uuid4().int % 1000000000)             # Token ID único
        
        # 3. Registrar o log simulando a transação blockchain
        logger.info(
            f" [BLOCKCHAIN MOCK] Emissão de NFT ERC-1155 com sucesso!\n"
            f"  - Learner: {learner_name} (ID: {learner_id})\n"
            f"  - Trail: {trail} | Level: {level}\n"
            f"  - Token ID: {token_id}\n"
            f"  - Contract: {DEFAULT_CONTRACT_ADDRESS}\n"
            f"  - Tx Hash: {tx_hash}\n"
            f"  - IPFS Metadata URL: ipfs://{ipfs_hash}\n"
            f"  - Metadata JSON: {json.dumps(ipfs_metadata)}"
        )

        return {
            "id": certificate_id,
            "learner_id": learner_id,
            "trail": trail,
            "level": level,
            "tx_hash": tx_hash,
            "contract_address": DEFAULT_CONTRACT_ADDRESS,
            "token_id": token_id,
            "metadata_url": f"ipfs://{ipfs_hash}",
            "ipfs_metadata": ipfs_metadata,
            "issued_at": datetime.datetime.now(datetime.timezone.utc)
        }
