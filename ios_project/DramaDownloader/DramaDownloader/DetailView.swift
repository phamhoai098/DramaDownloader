import SwiftUI
import AVKit

struct PlayerView: View {
    let episode: DramaEpisode
    let seriesName: String
    @Environment(\.dismiss) private var dismiss
    @State private var player: AVPlayer?
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            if let streamURLString = episode.directUrl, let streamURL = URL(string: streamURLString) {
                VideoPlayer(player: player)
                    .onAppear {
                        player = AVPlayer(url: streamURL)
                        player?.play()
                    }
                    .onDisappear {
                        player?.pause()
                    }
            } else {
                VStack(spacing: 12) {
                    Image(systemName: "lock.shield.fill")
                        .font(.system(size: 48))
                        .foregroundColor(.red)
                    Text("Tập phim này đang bị khóa VIP hoặc không có luồng phát trực tiếp.")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            }
        }
        .navigationTitle("EP\(episode.num): \(episode.title)")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct DetailView: View {
    let item: DramaCatalogItem
    @StateObject private var api = APIService.shared
    @State private var detail: DramaSeriesDetail?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedEpisode: DramaEpisode?
    
    let columns = [
        GridItem(.adaptive(minimum: 65, maximum: 80), spacing: 8)
    ]
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Header Banner
                HStack(alignment: .top, spacing: 14) {
                    if let coverStr = item.cover, let coverUrl = URL(string: coverStr) {
                        AsyncImage(url: coverUrl) { image in
                            image.resizable().aspectRatio(contentMode: .fill)
                        } placeholder: {
                            Color(white: 0.15)
                        }
                        .frame(width: 120, height: 165)
                        .cornerRadius(10)
                        .shadow(radius: 5)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text(item.name)
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .lineLimit(3)
                        
                        HStack(spacing: 6) {
                            Text(item.platform?.uppercased() ?? "OTT")
                                .font(.caption2)
                                .fontWeight(.bold)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.blue.opacity(0.8))
                                .cornerRadius(4)
                            
                            Text("🎬 \(item.episodes) tập")
                                .font(.caption)
                                .foregroundColor(.cyan)
                            
                            if let score = item.score {
                                Text("⭐ \(score)")
                                    .font(.caption)
                                    .foregroundColor(.yellow)
                            }
                        }
                        
                        if !item.tags.isEmpty {
                            Text(item.tags.joined(separator: ", "))
                                .font(.caption2)
                                .foregroundColor(.gray)
                                .lineLimit(2)
                        }
                    }
                }
                .padding(.horizontal)
                
                // Synopsis
                if let desc = detail?.description ?? item.desc, !desc.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Tóm tắt nội dung")
                            .font(.headline)
                            .foregroundColor(.white)
                        Text(desc)
                            .font(.footnote)
                            .foregroundColor(.gray)
                            .lineSpacing(3)
                    }
                    .padding(.horizontal)
                }
                
                Divider().background(Color(white: 0.2))
                
                // Episodes Grid
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text("Danh sách tập phim")
                            .font(.headline)
                            .foregroundColor(.white)
                        Spacer()
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .cyan))
                        }
                    }
                    
                    if let err = errorMessage {
                        Text(err)
                            .font(.footnote)
                            .foregroundColor(.red)
                    } else if let episodes = detail?.episodes {
                        LazyVGrid(columns: columns, spacing: 8) {
                            ForEach(episodes) { ep in
                                Button(action: {
                                    selectedEpisode = ep
                                }) {
                                    VStack(spacing: 2) {
                                        Text("Tập \(ep.num)")
                                            .font(.caption)
                                            .fontWeight(.semibold)
                                        if ep.locked && ep.directUrl == nil {
                                            Image(systemName: "lock.fill")
                                                .font(.system(size: 8))
                                                .foregroundColor(.red)
                                        }
                                    }
                                    .frame(maxWidth: .infinity, minHeight: 40)
                                    .background(ep.locked && ep.directUrl == nil ? Color(white: 0.12) : Color.blue.opacity(0.2))
                                    .foregroundColor(ep.locked && ep.directUrl == nil ? .gray : .cyan)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(ep.locked && ep.directUrl == nil ? Color(white: 0.2) : Color.blue.opacity(0.5), lineWidth: 1)
                                    )
                                    .cornerRadius(8)
                                }
                                .disabled(ep.locked && ep.directUrl == nil)
                            }
                        }
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical)
        }
        .background(Color(white: 0.05).ignoresSafeArea())
        .navigationTitle(item.name)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $selectedEpisode) { ep in
            NavigationView {
                PlayerView(episode: ep, seriesName: item.name)
            }
        }
        .task {
            do {
                detail = try await api.fetchSeriesDetail(target: item.link ?? item.id, platformHint: item.platform)
                isLoading = false
            } catch {
                errorMessage = "Không thể tải danh sách tập: \(error.localizedDescription)"
                isLoading = false
            }
        }
    }
}

