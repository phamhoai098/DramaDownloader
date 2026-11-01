import Foundation

class APIService: ObservableObject {
    static let shared = APIService()
    
    // Default to localhost, configurable via Settings
    @Published var serverBaseURL: String = "http://localhost:8000"
    
    let platforms: [DramaPlatform] = [
        DramaPlatform(id: "dramabox", name: "DramaBox", icon: "play.tv.fill"),
        DramaPlatform(id: "shortmax", name: "ShortMax", icon: "film.fill"),
        DramaPlatform(id: "netshort", name: "NetShort", icon: "sparkles.tv.fill"),
        DramaPlatform(id: "goodshort", name: "GoodShort", icon: "star.fill"),
        DramaPlatform(id: "freereels", name: "FreeReels", icon: "video.fill"),
        DramaPlatform(id: "kisskh", name: "KissKH", icon: "heart.fill"),
        DramaPlatform(id: "hongguo", name: "HongGuo", icon: "flame.fill"),
        DramaPlatform(id: "dramawave", name: "DramaWave", icon: "waveform"),
        DramaPlatform(id: "flextv", name: "FlexTV", icon: "tv.fill")
    ]
    
    func fetchCatalog(platform: String, language: String = "vi", query: String? = nil, page: Int = 1) async throws -> [DramaCatalogItem] {
        var components = URLComponents(string: "\(serverBaseURL)/api/catalog")
        var queryItems = [
            URLQueryItem(name: "platform", value: platform),
            URLQueryItem(name: "lang", value: language),
            URLQueryItem(name: "page", value: "\(page)")
        ]
        if let query = query, !query.isEmpty {
            queryItems.append(URLQueryItem(name: "q", value: query))
        }
        components?.queryItems = queryItems
        
        guard let url = components?.url else { throw URLError(.badURL) }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        struct CatalogResponse: Codable {
            let items: [DramaCatalogItem]
            let total: Int
        }
        
        let decoded = try JSONDecoder().decode(CatalogResponse.self, from: data)
        return decoded.items
    }
    
    func fetchSeriesDetail(target: String, platformHint: String? = nil) async throws -> DramaSeriesDetail {
        var components = URLComponents(string: "\(serverBaseURL)/api/inspect")
        var queryItems = [URLQueryItem(name: "url", value: target)]
        if let hint = platformHint {
            queryItems.append(URLQueryItem(name: "platform", value: hint))
        }
        components?.queryItems = queryItems
        
        guard let url = components?.url else { throw URLError(.badURL) }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        return try JSONDecoder().decode(DramaSeriesDetail.self, from: data)
    }
}

