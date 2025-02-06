import requests
from typing import Optional, List, Dict, Any

from agentsystem.models.Model import Model

class KoboldCPPModel(Model):
    pass
    

class KoboldCPPClientError(Exception):
    """Base exception for KoboldCPP client errors"""
    pass

class ServerBusyError(KoboldCPPClientError):
    """Exception raised when server is busy"""
    pass

class KoboldCPPClient:
    def __init__(self, base_url: str = "http://localhost:5001", timeout: int = 300):
        """
        Initialize the KoboldCpp API client
        
        :param base_url: Base URL of the KoboldCpp server
        :param timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def generate(
        self,
        prompt: str,
        max_context_length: Optional[int] = None,
        max_length: Optional[int] = None,
        rep_pen: Optional[float] = None,
        rep_pen_range: Optional[int] = None,
        temperature: Optional[float] = None,
        tfs: Optional[float] = None,
        top_a: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        min_p: Optional[float] = None,
        typical: Optional[float] = None,
        sampler_order: Optional[List[int]] = None,
        sampler_seed: Optional[int] = None,
        stop_sequence: Optional[List[str]] = None,
        use_default_badwordsids: Optional[bool] = None,
        dynatemp_range: Optional[float] = None,
        smoothing_factor: Optional[float] = None,
        dynatemp_exponent: Optional[float] = None,
        mirostat: Optional[int] = None,
        mirostat_tau: Optional[float] = None,
        mirostat_eta: Optional[float] = None,
        genkey: Optional[str] = None,
        grammar: Optional[str] = None,
        grammar_retain_state: Optional[bool] = None,
        memory: Optional[str] = None,
        images: Optional[List[str]] = None,
        trim_stop: Optional[bool] = None,
        render_special: Optional[bool] = None,
        bypass_eos: Optional[bool] = None,
        banned_tokens: Optional[List[str]] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        dry_multiplier: Optional[float] = None,
        dry_base: Optional[float] = None,
        dry_allowed_length: Optional[int] = None,
        dry_sequence_breakers: Optional[List[str]] = None,
        xtc_threshold: Optional[float] = None,
        xtc_probability: Optional[float] = None,
        logprobs: Optional[bool] = None,
    ) -> str:
        """
        Generate text using the KoboldCpp API
        
        :param prompt: The input prompt (required)
        :param max_context_length: Maximum number of tokens to send to the model
        :param max_length: Number of tokens to generate
        ... (other parameters match the API specification)
        
        :return: Generated text
        :raises ServerBusyError: If server returns 503 status
        :raises KoboldCPPClientError: For other API errors
        """
        url = f"{self.base_url}/api/v1/generate"
        payload = {"prompt": prompt}
        
        # Add optional parameters
        optional_params = {
            k: v for k, v in locals().items() 
            if k != 'self' and k != 'prompt' and v is not None
        }
        
        payload.update(optional_params)
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 503:
                error_detail = response.json().get('detail', {})
                raise ServerBusyError(error_detail.get('msg', 'Server is busy')) from err
            raise KoboldCPPClientError(f"API request failed: {err}") from err
        except requests.exceptions.RequestException as err:
            raise KoboldCPPClientError(f"Request failed: {err}") from err
            
        try:
            data = response.json()
            return data['results'][0]['text']
        except (KeyError, IndexError) as err:
            raise KoboldCPPClientError("Failed to parse response") from err

    def get_model(self) -> str:
        """Get the current model name"""
        return self._get_simple("/api/v1/model", "result")

    def get_version(self) -> str:
        """Get the KoboldAI United version"""
        return self._get_simple("/api/v1/info/version", "result")

    def get_max_context_length(self) -> int:
        """Get current max context length setting"""
        return self._get_simple("/api/v1/config/max_context_length", "value")

    def get_max_length(self) -> int:
        """Get current max generation length setting"""
        return self._get_simple("/api/v1/config/max_length", "value")

    def get_properties(self) -> dict:
        """Get model properties including Jinja template"""
        return self._get("/props")

    def _get_simple(self, endpoint: str, key: str) -> Any:
        """Helper for simple GET endpoints returning {key: value}"""
        data = self._get(endpoint)
        return data.get(key)

    def _get(self, endpoint: str) -> dict:
        """Generic GET request handler"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise KoboldCPPClientError(f"API request failed: {err}") from err
        except requests.exceptions.RequestException as err:
            raise KoboldCPPClientError(f"Request failed: {err}") from err
        except ValueError as err:
            raise KoboldCPPClientError("Failed to parse JSON response") from err

# Example usage
if __name__ == "__main__":
    client = KoboldCPPClient()
    
    try:
        response = client.generate(
            prompt="Once upon a time,",
            max_length=50,
            temperature=0.7,
            top_p=0.9
        )
        print("Generated text:", response)
        print("Current model:", client.get_model())
        print("Max context length:", client.get_max_context_length())
    except ServerBusyError as e:
        print("Server busy:", str(e))
    except KoboldCPPClientError as e:
        print("Error:", str(e))