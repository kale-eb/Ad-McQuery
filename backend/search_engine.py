import json
import numpy as np
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer


def create_embedding_text(analysis_data: Dict[str, Any]) -> str:
    """Convert analysis data into searchable text with weighted semantic keywords"""
    text_parts = []
    
    # Activity & Energy
    if analysis_data.get('activity_level') == 'dynamic':
        text_parts.append("fast-paced dynamic energetic active movement quick")
    elif analysis_data.get('activity_level') == 'sedentary':
        text_parts.append("slow-paced calm static peaceful relaxed")
    
    # Music intensity
    music = analysis_data.get('music_intensity', 'low')
    if music == 'high':
        text_parts.append("loud energetic upbeat fast music intense")
    elif music == 'medium':
        text_parts.append("moderate tempo balanced music")
    else:
        text_parts.append("soft calm quiet ambient peaceful music")
    
    # Scene cuts (high = fast-paced)
    scene_cuts = len(analysis_data.get('scene_cuts', []))
    if scene_cuts > 10:
        text_parts.append("fast-paced quick cuts rapid editing dynamic")
    elif scene_cuts > 5:
        text_parts.append("moderate pacing steady editing")
    else:
        text_parts.append("slow-paced few cuts long takes calm")
    
    # Emotional indices with weighted keywords based on strength
    indices_config = {
        'luxury_index': {
            'strong': 'luxury luxury luxury expensive expensive premium high-end wealthy exclusive elite sophisticated upscale',
            'weak': 'somewhat luxury expensive premium'
        },
        'success_index': {
            'strong': 'successful successful achievement wealthy accomplished winning triumph victory elite',
            'weak': 'somewhat successful achievement'
        },
        'family_index': {
            'strong': 'family family children parents togetherness belonging home loving caring',
            'weak': 'somewhat family children parents'
        },
        'adventure_index': {
            'strong': 'adventure adventure travel freedom exploration outdoor exciting thrilling journey',
            'weak': 'somewhat adventure travel outdoor'
        },
        'health_index': {
            'strong': 'healthy healthy fitness exercise wellness active energetic vibrant strong',
            'weak': 'somewhat healthy fitness exercise'
        },
        'comfort_index': {
            'strong': 'comfortable comfortable cozy relaxing peaceful homey warm soft gentle',
            'weak': 'somewhat comfortable cozy relaxing'
        },
        'humor_index': {
            'strong': 'funny funny comedy humorous entertaining laughs hilarious amusing playful',
            'weak': 'somewhat funny comedy humorous'
        },
        'love_index': {
            'strong': 'romantic romantic love dating relationships intimate affectionate tender',
            'weak': 'somewhat romantic love relationships'
        },
        'fear_index': {
            'strong': 'security security safety protection warning danger threatening serious urgent',
            'weak': 'somewhat security safety protection'
        },
        'nostalgia_index': {
            'strong': 'nostalgic nostalgic vintage retro classic memories sentimental timeless traditional',
            'weak': 'somewhat nostalgic vintage retro'
        }
    }
    
    # Apply weighted keywords based on index values
    for index_name, keywords in indices_config.items():
        value = analysis_data.get(index_name, 0)
        if value >= 0.6:  # Strong presence - highly weighted
            text_parts.append(keywords['strong'])
        elif value >= 0.2:  # Weak presence - lightly weighted
            text_parts.append(keywords['weak'])
    
    # Demographics
    age_demo = analysis_data.get('age_demographic')
    if age_demo and age_demo != 'N/A':
        text_parts.append(f"{age_demo} demographic {age_demo} audience")
    
    gender_demo = analysis_data.get('gender_demographic')
    if gender_demo and gender_demo != 'N/A':
        text_parts.append(f"{gender_demo} audience {gender_demo} demographic")
    
    # Product visibility
    visibility = analysis_data.get('product_visibility_score')
    if visibility == 'high':
        text_parts.append("product-focused prominent product visible showcasing")
    elif visibility == 'medium':
        text_parts.append("moderate product presence")
    elif visibility == 'low':
        text_parts.append("brand-awareness subtle product")
    
    # Purchase urgency
    urgency = analysis_data.get('purchase_urgency')
    if urgency == 'high':
        text_parts.append("urgent immediate action buy now")
    elif urgency == 'medium':
        text_parts.append("moderate call-to-action")
    elif urgency == 'low':
        text_parts.append("brand awareness informational")
    
    # Message types
    message_types = analysis_data.get('message_types', [])
    for msg_type in message_types:
        if msg_type == 'humor':
            text_parts.append("funny comedy humorous entertaining")
        elif msg_type == 'storytelling':
            text_parts.append("narrative story emotional journey")
        elif msg_type == 'demonstration':
            text_parts.append("showing product demo how-to practical")
        elif msg_type == 'emotional_appeal':
            text_parts.append("emotional touching heartfelt moving")
        elif msg_type == 'problem_solution':
            text_parts.append("solution problem-solving helpful practical")
    
    return " ".join(text_parts)


class AdSearchEngine:
    """Vector-based search engine for advertisement analysis results"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the search engine with a sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.metadata = []
        self.indexed = False
    
    def index_analysis_results(self, analysis_results: Dict[str, Dict[str, Any]]):
        """Index all analysis results for vector search"""
        print(f"Indexing {len(analysis_results)} advertisement analyses...")
        
        embeddings_list = []
        self.metadata = []
        
        for filename, data in analysis_results.items():
            # Skip files with errors
            if 'error' in data or 'analysis_error' in data:
                continue
                
            # Create searchable text representation
            search_text = create_embedding_text(data)
            
            # Generate embedding
            embedding = self.model.encode(search_text)
            
            embeddings_list.append(embedding)
            self.metadata.append({
                'filename': filename,
                'search_text': search_text,
                'analysis_data': data,
                'file_type': 'video' if filename.lower().endswith('.mp4') else 'image'
            })
        
        self.embeddings = np.array(embeddings_list)
        self.indexed = True
        print(f"Successfully indexed {len(self.metadata)} files")
    
    def search(self, query: str, top_k: int = 10, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for ads matching the query
        
        Args:
            query: Search query (e.g., "upbeat fast paced", "wealthy luxury")
            top_k: Number of results to return
            file_type: Filter by 'video', 'image', or None for both
        
        Returns:
            List of search results with similarity scores
        """
        if not self.indexed:
            raise ValueError("Search engine not indexed. Call index_analysis_results() first.")
        
        # Embed the query
        query_embedding = self.model.encode(query)
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get all results with similarity scores
        results = []
        for idx, similarity in enumerate(similarities):
            metadata = self.metadata[idx]
            
            # Apply file type filter if specified
            if file_type and metadata['file_type'] != file_type:
                continue
                
            results.append({
                'filename': metadata['filename'],
                'file_type': metadata['file_type'],
                'similarity': float(similarity),
                'analysis': metadata['analysis_data'],
                'search_text_preview': metadata['search_text'][:200] + "..."
            })
        
        # Sort by similarity (highest first) and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def search_with_filters(self, 
                          query: str, 
                          filters: Optional[Dict[str, Any]] = None, 
                          top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search with additional numerical/categorical filters
        
        Args:
            query: Search query
            filters: Dict of filters like {'min_luxury_index': 0.5, 'activity_level': 'dynamic'}
            top_k: Number of results to return
        """
        # Get more results initially to apply filters
        initial_results = self.search(query, top_k=50)
        
        if not filters:
            return initial_results[:top_k]
        
        filtered_results = []
        for result in initial_results:
            data = result['analysis']
            
            # Apply all filters
            passes_filters = True
            for filter_key, filter_value in filters.items():
                if filter_key.startswith('min_'):
                    # Minimum value filters (e.g., min_luxury_index)
                    index_name = filter_key[4:]  # Remove 'min_' prefix
                    if data.get(index_name, 0) < filter_value:
                        passes_filters = False
                        break
                elif filter_key.startswith('max_'):
                    # Maximum value filters (e.g., max_luxury_index)
                    index_name = filter_key[4:]  # Remove 'max_' prefix
                    if data.get(index_name, 0) > filter_value:
                        passes_filters = False
                        break
                else:
                    # Exact match filters (e.g., activity_level)
                    if data.get(filter_key) != filter_value:
                        passes_filters = False
                        break
            
            if passes_filters:
                filtered_results.append(result)
                
            # Stop when we have enough results
            if len(filtered_results) >= top_k:
                break
        
        return filtered_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed data"""
        if not self.indexed:
            return {"error": "Not indexed"}
        
        total_videos = sum(1 for m in self.metadata if m['file_type'] == 'video')
        total_images = sum(1 for m in self.metadata if m['file_type'] == 'image')
        
        return {
            "total_files": len(self.metadata),
            "total_videos": total_videos,
            "total_images": total_images,
            "embedding_dimension": self.embeddings.shape[1]
        }


def load_and_search(analysis_file: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to load analysis results and search"""
    # Load analysis results
    with open(analysis_file, 'r') as f:
        analysis_results = json.load(f)
    
    # Create and index search engine
    search_engine = AdSearchEngine()
    search_engine.index_analysis_results(analysis_results)
    
    # Search
    return search_engine.search(query, top_k)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python search_engine.py <analysis_results.json> <query> [top_k]")
        print("\nExamples:")
        print("  python search_engine.py batch_test.json 'upbeat fast paced'")
        print("  python search_engine.py batch_test.json 'wealthy luxury expensive'")
        print("  python search_engine.py batch_test.json 'funny comedy' 10")
        sys.exit(1)
    
    analysis_file = sys.argv[1]
    query = sys.argv[2]
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    try:
        results = load_and_search(analysis_file, query, top_k)
        
        print(f"\n🔍 Search Results for: '{query}'")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['filename']} ({result['file_type']})")
            print(f"   Similarity: {result['similarity']:.3f}")
            
            # Show relevant analysis data
            analysis = result['analysis']
            indices = ['luxury_index', 'success_index', 'humor_index', 'comfort_index', 
                      'adventure_index', 'family_index', 'health_index']
            
            relevant_indices = []
            for idx in indices:
                value = analysis.get(idx, 0)
                if value >= 0.2:
                    relevant_indices.append(f"{idx}: {value:.1f}")
            
            if relevant_indices:
                print(f"   Key indices: {', '.join(relevant_indices)}")
            
            if analysis.get('activity_level'):
                print(f"   Activity: {analysis['activity_level']}")
            if analysis.get('music_intensity'):
                print(f"   Music: {analysis['music_intensity']}")
        
        if not results:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")