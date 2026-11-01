import Foundation

struct DramaCatalogItem: Identifiable, Codable {
    let id: String
    let name: String
    let cover: String?
    let episodes: Int
    let score: String?
    let tags: [String]
    let desc: String?
    let link: String?
    let platform: String?
}

struct DramaEpisode: Identifiable, Codable {
    var id: Int { num }
    let num: Int
    let title: String
    let url: String
    let directUrl: String?
    let thumb: String?
    let locked: Bool
    let subs: [DramaSubtitle]
}

struct DramaSubtitle: Identifiable, Codable {
    var id: String { "\(lang)_\(url)" }
    let lang: String
    let name: String
    let url: String
}

struct DramaSeriesDetail: Identifiable, Codable {
    let id: String
    let name: String
    let platform: String
    let cover: String?
    let description: String?
    let episodeCount: Int
    let accessibleCount: Int
    let episodes: [DramaEpisode]
    let url: String?
}

struct DramaPlatform: Identifiable {
    let id: String
    let name: String
    let icon: String
}

