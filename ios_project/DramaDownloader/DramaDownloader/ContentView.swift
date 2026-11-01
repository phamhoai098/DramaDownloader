import SwiftUI

struct ContentView: View {
    @StateObject private var api = APIService.shared
    @State private var selectedPlatform: String = "dramabox"
    @State private var items: [DramaCatalogItem] = []
    @State private var isLoading = false
    @State private var searchText = ""
    @State private var selectedLanguage = "vi"
    @State private var currentPage = 1
    
    let columns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Platform Horizontal Selector
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(api.platforms) { p in
                            Button(action: {
                                selectedPlatform = p.id
                                currentPage = 1
                                loadCatalog(page: 1)
                            }) {
                                HStack(spacing: 6) {
                                    Image(systemName: p.icon)
                                    Text(p.name)
                                        .font(.caption)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(selectedPlatform == p.id ? Color.cyan : Color(white: 0.15))
                                .foregroundColor(selectedPlatform == p.id ? .black : .white)
                                .cornerRadius(20)
                            }
                        }
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                }
                .background(Color(white: 0.08))
                
                // Drama Grid
                if isLoading {
                    Spacer()
                    ProgressView("Đang tải danh mục phim...")
                        .progressViewStyle(CircularProgressViewStyle(tint: .cyan))
                        .foregroundColor(.gray)
                    Spacer()
                } else if items.isEmpty {
                    Spacer()
                    VStack(spacing: 8) {
                        Image(systemName: "film")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        Text("Không có phim nào để hiển thị.")
                            .foregroundColor(.gray)
                    }
                    Spacer()
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 14) {
                            ForEach(items) { item in
                                NavigationLink(destination: DetailView(item: item)) {
                                    DramaCard(item: item)
                                }
                            }
                        }
                        .padding(12)
                        
                        // Pagination Bar
                        HStack(spacing: 16) {
                            Button(action: {
                                if currentPage > 1 {
                                    currentPage -= 1
                                    loadCatalog(page: currentPage)
                                }
                            }) {
                                HStack {
                                    Image(systemName: "chevron.left")
                                    Text("Trang trước")
                                }
                                .font(.caption)
                                .fontWeight(.semibold)
                                .padding(.horizontal, 14)
                                .padding(.vertical, 8)
                                .background(currentPage > 1 ? Color(white: 0.2) : Color(white: 0.1))
                                .foregroundColor(currentPage > 1 ? .white : .gray)
                                .cornerRadius(10)
                            }
                            .disabled(currentPage <= 1)
                            
                            Text("Trang \(currentPage)")
                                .font(.caption)
                                .fontWeight(.bold)
                                .foregroundColor(.cyan)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.cyan.opacity(0.15))
                                .cornerRadius(8)
                            
                            Button(action: {
                                currentPage += 1
                                loadCatalog(page: currentPage)
                            }) {
                                HStack {
                                    Text("Trang sau")
                                    Image(systemName: "chevron.right")
                                }
                                .font(.caption)
                                .fontWeight(.semibold)
                                .padding(.horizontal, 14)
                                .padding(.vertical, 8)
                                .background(Color.cyan)
                                .foregroundColor(.black)
                                .cornerRadius(10)
                            }
                        }
                        .padding(.vertical, 16)
                    }
                }
            }
            .background(Color(white: 0.05).ignoresSafeArea())
            .navigationTitle("Drama Downloader")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $searchText, prompt: "Tìm kiếm phim...")
            .onSubmit(of: .search) {
                currentPage = 1
                loadCatalog(page: 1)
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    HStack(spacing: 4) {
                        Text(selectedLanguage == "vi" ? "Phụ đề:" : "Subtitle:")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.secondary)
                        Picker("Phụ đề / Subtitle", selection: $selectedLanguage) {
                            Text("🇻🇳 VI").tag("vi")
                            Text("🇬🇧 EN").tag("en")
                        }
                        .pickerStyle(.menu)
                    }
                    .onChange(of: selectedLanguage) { _ in
                        currentPage = 1
                        loadCatalog(page: 1)
                    }
                }
            }
            .onAppear {
                if items.isEmpty {
                    loadCatalog(page: 1)
                }
            }
        }
    }
    
    private func loadCatalog(page: Int = 1) {
        isLoading = true
        Task {
            do {
                let fetched = try await api.fetchCatalog(
                    platform: selectedPlatform,
                    language: selectedLanguage,
                    query: searchText.isEmpty ? nil : searchText,
                    page: page
                )
                await MainActor.run {
                    items = fetched
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                }
            }
        }
    }
}

struct DramaCard: View {
    let item: DramaCatalogItem
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            ZStack(alignment: .topTrailing) {
                if let coverStr = item.cover, let coverUrl = URL(string: coverStr) {
                    AsyncImage(url: coverUrl) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Color(white: 0.12)
                    }
                    .frame(height: 220)
                    .clipped()
                    .cornerRadius(8)
                } else {
                    Rectangle()
                        .fill(Color(white: 0.15))
                        .frame(height: 220)
                        .cornerRadius(8)
                }
                
                if let score = item.score {
                    Text("⭐ \(score)")
                        .font(.caption2)
                        .fontWeight(.bold)
                        .padding(4)
                        .background(Color.black.opacity(0.7))
                        .foregroundColor(.yellow)
                        .cornerRadius(4)
                        .padding(6)
                }
            }
            
            Text(item.name)
                .font(.footnote)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .lineLimit(2)
                .multilineTextAlignment(.leading)
            
            Text("🎬 \(item.episodes) tập")
                .font(.caption2)
                .foregroundColor(.cyan)
        }
        .padding(8)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

